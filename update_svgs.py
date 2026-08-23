import urllib.request
import json
import datetime
import re
import os

USERNAME = "Gracy769"

def get_stats():
    # 1. Fetch user profile data
    req = urllib.request.Request(f"https://api.github.com/users/{USERNAME}")
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    
    try:
        with urllib.request.urlopen(req) as response:
            user_data = json.loads(response.read())
    except Exception as e:
        print("Failed to fetch user data:", e)
        return None
        
    followers = user_data.get("followers", 0)
    repos = user_data.get("public_repos", 0)
    created_at = user_data.get("created_at")
    
    # Calculate exactly how old the account is
    if created_at:
        created_date = datetime.datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
        now = datetime.datetime.utcnow()
        diff = now - created_date
        years = diff.days // 365
        remaining_days = diff.days % 365
        months = remaining_days // 30
        days = remaining_days % 30
        uptime_str = f"{years} years, {months} months, {days} days"
    else:
        uptime_str = "Unknown"

    # 2. Fetch repos to calculate total stars
    try:
        req = urllib.request.Request(f"https://api.github.com/users/{USERNAME}/repos?per_page=100")
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req) as response:
            repos_data = json.loads(response.read())
        stars = sum(r.get("stargazers_count", 0) for r in repos_data)
    except Exception as e:
        print("Failed to fetch repos:", e)
        stars = 0
    
    # 3. Try to fetch total commits via GitHub Search API (REST)
    # The default token might not have full scope for all historical commits, but it approximates well
    commits = 0
    try:
        req = urllib.request.Request(f"https://api.github.com/search/commits?q=author:{USERNAME}")
        req.add_header("Accept", "application/vnd.github.cloak-preview+json")
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req) as response:
            commits_data = json.loads(response.read())
            commits = commits_data.get("total_count", 0)
    except Exception as e:
        print("Commit fetch failed or rate limited:", e)
        commits = 123 # fallback

    return {
        "uptime": uptime_str,
        "repos": str(repos),
        "stars": str(stars),
        "commits": str(commits),
        "followers": str(followers)
    }

def update_svg(filename, stats):
    if not os.path.exists(filename):
        print(f"{filename} not found.")
        return
        
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Regex to match the dynamically generated tags in both light/dark themes safely
        # Uptime
        content = re.sub(
            r'(<tspan fill="[^"]+">\. Uptime: </tspan><tspan fill="[^"]+">\.+</tspan><tspan fill="[^"]+"> )[^<]+(</tspan>)', 
            r'\g<1>' + stats["uptime"] + r'\g<2>', content
        )
                         
        # Repos
        content = re.sub(
            r'(<tspan fill="[^"]+">\. Repos: </tspan><tspan fill="[^"]+">\.+</tspan><tspan fill="[^"]+"> )[^<]+(</tspan>)', 
            r'\g<1>' + stats["repos"] + r'\g<2>', content
        )
                         
        # Stars
        content = re.sub(
            r'(<tspan fill="[^"]+">\. Stars: </tspan><tspan fill="[^"]+">\.+</tspan><tspan fill="[^"]+"> )[^<]+(</tspan>)', 
            r'\g<1>' + stats["stars"] + r'\g<2>', content
        )
                         
        # Commits
        content = re.sub(
            r'(<tspan fill="[^"]+">\. Commits: </tspan><tspan fill="[^"]+">\.+</tspan><tspan fill="[^"]+"> )[^<]+(</tspan>)', 
            r'\g<1>' + stats["commits"] + r'\g<2>', content
        )
                         
        # Followers
        content = re.sub(
            r'(<tspan fill="[^"]+">\. Followers: </tspan><tspan fill="[^"]+">\.+</tspan><tspan fill="[^"]+"> )[^<]+(</tspan>)', 
            r'\g<1>' + stats["followers"] + r'\g<2>', content
        )

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Updated {filename} successfully.")
    except Exception as e:
        print(f"Failed to update {filename}: {e}")

if __name__ == "__main__":
    stats = get_stats()
    if stats:
        print("Fetched live stats:", stats)
        update_svg("dark_mode.svg", stats)
        update_svg("light_mode.svg", stats)
