import urllib.request
import json
import datetime
import re
import os

USERNAME = "Gracy769"

def graphql_query(query, token):
    req = urllib.request.Request("https://api.github.com/graphql", method="POST")
    req.add_header("Authorization", f"bearer {token}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, data=json.dumps({"query": query}).encode('utf-8')) as response:
        return json.loads(response.read())

def get_stats():
    # Use PAT_TOKEN for private repo access, fallback to GITHUB_TOKEN
    token = os.environ.get("PAT_TOKEN")
    if not token:
        token = os.environ.get("GITHUB_TOKEN")
        print("Warning: PAT_TOKEN not found, using default GITHUB_TOKEN (private stats won't be counted).")
    
    # 1. Fetch user data (repos, followers, uptime)
    req = urllib.request.Request("https://api.github.com/user")
    req.add_header("Authorization", f"token {token}")
    try:
        with urllib.request.urlopen(req) as response:
            user_data = json.loads(response.read())
            
        followers = user_data.get("followers", 0)
        # Using authenticated /user endpoint gives private repos too
        repos = user_data.get("public_repos", 0) + user_data.get("total_private_repos", 0)
        created_at = user_data.get("created_at")
    except Exception as e:
        print("Failed to fetch user REST data:", e)
        return None

    # Calculate Uptime
    created_date = datetime.datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
    now = datetime.datetime.utcnow()
    diff = now - created_date
    years = diff.days // 365
    remaining_days = diff.days % 365
    months = remaining_days // 30
    days = remaining_days % 30
    uptime_str = f"{years} years, {months} months, {days} days"

    # 2. Fetch Stars (REST - gets both private and public if token allows)
    try:
        req = urllib.request.Request("https://api.github.com/user/repos?per_page=100&affiliation=owner")
        req.add_header("Authorization", f"token {token}")
        with urllib.request.urlopen(req) as response:
            repos_data = json.loads(response.read())
        stars = sum(r.get("stargazers_count", 0) for r in repos_data)
    except Exception as e:
        print("Failed to fetch repos for stars:", e)
        stars = 0

    # 3. Fetch All-Time Commits (GraphQL) across all years
    total_commits = 0
    start_year = created_date.year
    current_year = now.year

    for year in range(start_year, current_year + 1):
        from_date = f"{year}-01-01T00:00:00Z"
        to_date = f"{year}-12-31T23:59:59Z"
        
        query = f"""
        query {{
          viewer {{
            contributionsCollection(from: "{from_date}", to: "{to_date}") {{
              totalCommitContributions
              restrictedContributionsCount
            }}
          }}
        }}
        """
        try:
            data = graphql_query(query, token)
            coll = data['data']['viewer']['contributionsCollection']
            # restrictedContributionsCount are private contributions. totalCommitContributions are public.
            total_commits += coll['totalCommitContributions'] + coll['restrictedContributionsCount']
        except Exception as e:
            print(f"Failed to fetch commits for {year}:", e)

    return {
        "uptime": uptime_str,
        "repos": str(repos),
        "stars": str(stars),
        "commits": str(total_commits),
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
        content = re.sub(r'(<tspan fill="[^"]+">\. Uptime: </tspan><tspan fill="[^"]+">\.+</tspan><tspan fill="[^"]+"> )[^<]+(</tspan>)', r'\g<1>' + stats["uptime"] + r'\g<2>', content)
        content = re.sub(r'(<tspan fill="[^"]+">\. Repos: </tspan><tspan fill="[^"]+">\.+</tspan><tspan fill="[^"]+"> )[^<]+(</tspan>)', r'\g<1>' + stats["repos"] + r'\g<2>', content)
        content = re.sub(r'(<tspan fill="[^"]+">\. Stars: </tspan><tspan fill="[^"]+">\.+</tspan><tspan fill="[^"]+"> )[^<]+(</tspan>)', r'\g<1>' + stats["stars"] + r'\g<2>', content)
        content = re.sub(r'(<tspan fill="[^"]+">\. Commits: </tspan><tspan fill="[^"]+">\.+</tspan><tspan fill="[^"]+"> )[^<]+(</tspan>)', r'\g<1>' + stats["commits"] + r'\g<2>', content)
        content = re.sub(r'(<tspan fill="[^"]+">\. Followers: </tspan><tspan fill="[^"]+">\.+</tspan><tspan fill="[^"]+"> )[^<]+(</tspan>)', r'\g<1>' + stats["followers"] + r'\g<2>', content)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Updated {filename} successfully.")
    except Exception as e:
        print(f"Failed to update {filename}: {e}")

if __name__ == "__main__":
    stats = get_stats()
    if stats:
        print("Fetched live accurate stats:", stats)
        update_svg("dark_mode.svg", stats)
        update_svg("light_mode.svg", stats)
