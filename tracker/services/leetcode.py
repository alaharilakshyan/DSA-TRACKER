import json
import re
import urllib.request
import urllib.error
from tracker.models import Problem, Topic

LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql/"

PATTERN_TAG_MAP = {
    "two-pointers": Problem.Pattern.TWO_POINTER,
    "sliding-window": Problem.Pattern.SLIDING_WINDOW,
    "monotonic-stack": Problem.Pattern.MONOTONIC_STACK,
    "monotonic-queue": Problem.Pattern.MONOTONIC_STACK,
    "dynamic-programming": Problem.Pattern.DP,
    "backtracking": Problem.Pattern.BACKTRACKING,
    "greedy": Problem.Pattern.GREEDY,
    "graph": Problem.Pattern.GRAPH,
    "breadth-first-search": Problem.Pattern.GRAPH,
    "depth-first-search": Problem.Pattern.GRAPH,
    "union-find": Problem.Pattern.UNION_FIND,
    "binary-search": Problem.Pattern.BINARY_SEARCH,
    "heap-priority-queue": Problem.Pattern.HEAP_TOP_K,
    "tree": Problem.Pattern.TREE_TRAVERSAL,
    "binary-tree": Problem.Pattern.TREE_TRAVERSAL,
    "trie": Problem.Pattern.TRIE,
    "bit-manipulation": Problem.Pattern.BIT_MANIPULATION,
}


def extract_slug(input_str: str) -> str:
    """Extracts problem slug from a URL or raw slug string."""
    cleaned = input_str.strip().rstrip("/")
    # Match https://leetcode.com/problems/<slug>/...
    match = re.search(r"leetcode\.com/problems/([^/?#]+)", cleaned, re.IGNORECASE)
    if match:
        return match.group(1).lower()
    # Otherwise treat as slug directly
    slug_match = re.search(r"^[a-zA-Z0-9\-]+$", cleaned)
    if slug_match:
        return cleaned.lower()
    return cleaned.split("/")[-1].lower()


def fetch_leetcode_problem(url_or_slug: str) -> dict:
    """
    Fetches problem metadata from LeetCode's public GraphQL API.
    Returns dictionary with parsed title, difficulty, pattern, matched topic, link, and hints.
    """
    slug = extract_slug(url_or_slug)
    if not slug:
        return {"error": "Invalid LeetCode URL or problem slug."}

    query = """
    query getQuestionDetail($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        questionFrontendId
        title
        titleSlug
        difficulty
        topicTags {
          name
          slug
        }
        hints
      }
    }
    """

    payload = json.dumps({
        "query": query,
        "variables": {"titleSlug": slug}
    }).encode("utf-8")

    req = urllib.request.Request(
        LEETCODE_GRAPHQL_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://leetcode.com",
            "Accept": "application/json",
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            res_data = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as e:
        return {"error": f"Failed to connect to LeetCode API: {str(e)}"}
    except Exception as e:
        return {"error": f"Error fetching problem: {str(e)}"}

    question = res_data.get("data", {}).get("question")
    if not question:
        return {"error": f"Problem '{slug}' not found on LeetCode."}

    title = question.get("title", "")
    difficulty_raw = question.get("difficulty", "MEDIUM").upper()
    difficulty = difficulty_raw if difficulty_raw in dict(Problem.Difficulty.choices) else Problem.Difficulty.MEDIUM
    tags = question.get("topicTags", [])
    hints = question.get("hints", [])

    # Infer Algorithmic Pattern
    inferred_pattern = Problem.Pattern.OTHER
    for tag in tags:
        tag_slug = tag.get("slug", "").lower()
        if tag_slug in PATTERN_TAG_MAP:
            inferred_pattern = PATTERN_TAG_MAP[tag_slug]
            break

    # Match Topic from database
    matched_topic = None
    for tag in tags:
        tag_name = tag.get("name", "")
        tag_slug = tag.get("slug", "")
        # Try matching by slug or name
        topic = (
            Topic.objects.filter(slug__iexact=tag_slug).first() or
            Topic.objects.filter(name__iexact=tag_name).first() or
            Topic.objects.filter(name__icontains=tag_name).first()
        )
        if topic:
            matched_topic = topic
            break

    # If no specific match, default to first available topic or Arrays
    if not matched_topic:
        matched_topic = Topic.objects.filter(slug="arrays").first() or Topic.objects.first()

    # Collect supporting concepts from remaining tags
    supporting = []
    primary_label = Problem.Pattern(inferred_pattern).label if inferred_pattern in dict(Problem.Pattern.choices) else ""
    for t in tags:
        t_name = t.get("name", "")
        if t_name and t_name.lower() != primary_label.lower() and t_name not in supporting:
            supporting.append(t_name)
    supporting_concepts_str = ", ".join(supporting[:4])

    canonical_link = f"https://leetcode.com/problems/{slug}/"
    notes_hint = ""
    if hints:
        notes_hint = "LeetCode Hints:\n" + "\n".join(f"- {h}" for h in hints[:3])

    return {
        "success": True,
        "frontend_id": question.get("questionFrontendId"),
        "title": title,
        "slug": slug,
        "difficulty": difficulty,
        "pattern": inferred_pattern,
        "supporting_concepts": supporting_concepts_str,
        "topic_id": matched_topic.id if matched_topic else None,
        "topic_name": matched_topic.name if matched_topic else "",
        "link": canonical_link,
        "tags": [t.get("name") for t in tags],
        "notes": notes_hint,
    }


def extract_username_from_url(input_str: str) -> str:
    """
    Extracts a LeetCode username from a profile URL or raw username/handle.
    Supports formats such as:
      - https://leetcode.com/u/username/
      - https://leetcode.com/u/username
      - https://leetcode.com/username/
      - https://leetcode.com/username
      - leetcode.com/u/username
      - https://leetcode.cn/u/username
      - @username
      - username
    """
    if not input_str:
        return ""
    cleaned = input_str.strip()
    # Strip URL fragments and query params
    cleaned = re.sub(r"[?#].*$", "", cleaned).rstrip("/")

    # Match /u/<username>
    u_match = re.search(r"leetcode\.(?:com|cn)/u/([^/?#]+)", cleaned, re.IGNORECASE)
    if u_match:
        return u_match.group(1).strip()

    # Match https://leetcode.com/<username> (excluding known reserved routes)
    reserved = {
        "problems", "contest", "explore", "discuss", "studyplan",
        "problemset", "company", "interview", "tag", "assessment",
        "subscribe", "accounts", "progress"
    }
    direct_match = re.search(r"leetcode\.(?:com|cn)/([^/?#]+)", cleaned, re.IGNORECASE)
    if direct_match:
        cand = direct_match.group(1).strip()
        if cand.lower() not in reserved:
            return cand

    # Match @username
    if cleaned.startswith("@"):
        return cleaned[1:].strip()

    # If the user pasted a path or plain username
    parts = [p for p in cleaned.split("/") if p]
    if parts:
        last = parts[-1]
        return last.lstrip("@").strip()

    return cleaned


# Mapping from LeetCode tag slugs to Smart DSA Tracker core Topic slugs
LEETCODE_TAG_TO_CORE_TOPIC = {
    "array": "arrays",
    "matrix": "arrays",
    "string": "strings",
    "linked-list": "linked-lists",
    "stack": "stacks-queues",
    "queue": "stacks-queues",
    "monotonic-stack": "stacks-queues",
    "monotonic-queue": "stacks-queues",
    "tree": "trees",
    "binary-tree": "trees",
    "binary-search-tree": "binary-search-trees",
    "heap-priority-queue": "heaps",
    "graph": "graphs",
    "depth-first-search": "graphs",
    "breadth-first-search": "graphs",
    "union-find": "graphs",
    "shortest-path": "graphs",
    "topological-sort": "graphs",
    "dynamic-programming": "dynamic-programming",
    "memoization": "dynamic-programming",
    "backtracking": "backtracking",
    "greedy": "greedy",
    "binary-search": "binary-search",
    "bit-manipulation": "bit-manipulation",
    "bitmask": "bit-manipulation",
    "trie": "tries",
    "two-pointers": "two-pointers",
    "sliding-window": "sliding-window",
}


def fetch_leetcode_user_profile(url_or_username: str, limit: int = 20) -> dict:
    """
    Fetches user public stats, solved topics, and recent accepted submissions
    from official LeetCode via GraphQL.
    Accepts either a full profile URL (e.g. https://leetcode.com/u/lee215/) or username.
    """
    username = extract_username_from_url(url_or_username)
    if not username:
        return {"error": "Please provide a valid LeetCode account URL or username."}

    query = """
    query userProfileStats($username: String!, $limit: Int!) {
      matchedUser(username: $username) {
        username
        profile {
          ranking
          reputation
          realName
          userAvatar
        }
        submitStats {
          acSubmissionNum {
            difficulty
            count
          }
        }
        tagProblemCounts {
          advanced {
            tagName
            tagSlug
            problemsSolved
          }
          intermediate {
            tagName
            tagSlug
            problemsSolved
          }
          fundamental {
            tagName
            tagSlug
            problemsSolved
          }
        }
      }
      recentAcSubmissionList(username: $username, limit: $limit) {
        id
        title
        titleSlug
        timestamp
      }
    }
    """

    payload = json.dumps({
        "query": query,
        "variables": {"username": username, "limit": limit}
    }).encode("utf-8")

    req = urllib.request.Request(
        LEETCODE_GRAPHQL_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://leetcode.com",
            "Accept": "application/json",
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            res_data = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as e:
        return {"error": f"Failed to connect to official LeetCode API: {str(e)}"}
    except Exception as e:
        return {"error": f"Error fetching LeetCode profile: {str(e)}"}

    matched = res_data.get("data", {}).get("matchedUser")
    if not matched:
        return {"error": f"LeetCode account for '{username}' was not found. Please verify your profile URL or handle."}

    profile = matched.get("profile", {}) or {}
    ranking = profile.get("ranking")
    real_name = profile.get("realName", "") or ""
    avatar_url = profile.get("userAvatar", "") or ""
    canonical_username = matched.get("username", username)
    canonical_profile_url = f"https://leetcode.com/u/{canonical_username}/"

    # Difficulty statistics
    submit_stats = matched.get("submitStats", {}).get("acSubmissionNum", [])
    diff_counts = {"All": 0, "Easy": 0, "Medium": 0, "Hard": 0}
    for stat in submit_stats:
        d = stat.get("difficulty")
        if d in diff_counts:
            diff_counts[d] = stat.get("count", 0)

    # Topic problem counts (Fundamental, Intermediate, Advanced)
    tag_problem_counts = matched.get("tagProblemCounts") or {}
    topics_solved = []
    core_topic_counts = {}

    for category in ["fundamental", "intermediate", "advanced"]:
        category_label = category.capitalize()
        for tag in tag_problem_counts.get(category, []):
            solved = tag.get("problemsSolved", 0)
            if solved > 0:
                name = tag.get("tagName", "")
                slug = tag.get("tagSlug", "")
                topics_solved.append({
                    "name": name,
                    "slug": slug,
                    "solved": solved,
                    "category": category_label,
                })
                # Check mapping to core topics
                core_slug = LEETCODE_TAG_TO_CORE_TOPIC.get(slug.lower())
                if core_slug:
                    core_topic_counts[core_slug] = core_topic_counts.get(core_slug, 0) + solved

    # Sort topics by solved count descending
    topics_solved.sort(key=lambda x: x["solved"], reverse=True)

    recent_submissions = res_data.get("data", {}).get("recentAcSubmissionList", [])

    return {
        "success": True,
        "username": canonical_username,
        "profile_url": canonical_profile_url,
        "ranking": ranking,
        "real_name": real_name,
        "avatar_url": avatar_url,
        "total_solved": diff_counts["All"],
        "easy": diff_counts["Easy"],
        "medium": diff_counts["Medium"],
        "hard": diff_counts["Hard"],
        "topics_solved": topics_solved,
        "topics_count": len(topics_solved),
        "core_topic_counts": core_topic_counts,
        "recent_submissions": recent_submissions,
    }


def sync_leetcode_for_user(user, url_or_username: str, limit: int = 20) -> dict:
    """
    Reads the user's LeetCode account URL or username, queries the official LeetCode GraphQL API,
    extracts user data, and syncs:
      1. Number of solved problems (Total, Easy, Medium, Hard) & ranking
      2. List of topics solved with exact problem counts per topic
      3. Recent accepted submissions auto-imported into Problem & Attempt records
    """
    from datetime import datetime, timezone as dt_tz
    from django.utils import timezone
    from tracker.models import Attempt, RevisionSchedule

    profile_data = fetch_leetcode_user_profile(url_or_username, limit=limit)
    if "error" in profile_data:
        return {"success": False, "error": profile_data["error"]}

    # Update UserProfile model
    if hasattr(user, "profile"):
        p = user.profile
        p.leetcode_username = profile_data["username"]
        p.leetcode_profile_url = profile_data["profile_url"]
        p.leetcode_avatar_url = profile_data.get("avatar_url", "")
        p.leetcode_real_name = profile_data.get("real_name", "")
        p.leetcode_ranking = profile_data["ranking"]
        p.leetcode_solved_count = profile_data["total_solved"]
        p.leetcode_easy_count = profile_data["easy"]
        p.leetcode_medium_count = profile_data["medium"]
        p.leetcode_hard_count = profile_data["hard"]
        p.leetcode_topic_stats = profile_data.get("topics_solved", [])
        p.leetcode_last_synced = timezone.now()
        p.save()

    new_problems_added = 0
    new_attempts_added = 0
    synced_titles = []

    for sub in profile_data.get("recent_submissions", []):
        title = sub.get("title", "").strip()
        slug = sub.get("titleSlug", "").strip()
        timestamp_str = sub.get("timestamp")

        if not title:
            continue

        # Check if problem already exists for this user
        problem = Problem.objects.filter(user=user, title__iexact=title).first()
        if not problem and slug:
            # Also try matching by canonical link
            problem = Problem.objects.filter(user=user, link__icontains=slug).first()

        solved_datetime = timezone.now()
        if timestamp_str and timestamp_str.isdigit():
            try:
                solved_datetime = datetime.fromtimestamp(int(timestamp_str), tz=dt_tz.utc)
            except Exception:
                pass

        if not problem:
            # Fetch problem metadata from LeetCode
            meta = fetch_leetcode_problem(slug or title)
            topic = None
            if meta.get("topic_id"):
                topic = Topic.objects.filter(id=meta["topic_id"]).first()
            if not topic:
                topic = Topic.objects.filter(slug="arrays").first() or Topic.objects.first()

            pattern = meta.get("pattern", Problem.Pattern.OTHER)
            difficulty = meta.get("difficulty", Problem.Difficulty.MEDIUM)
            link = meta.get("link", f"https://leetcode.com/problems/{slug}/" if slug else "")
            notes = meta.get("notes", f"Auto-synced from LeetCode account @{profile_data['username']}.")

            problem = Problem.objects.create(
                user=user,
                title=title,
                topic=topic,
                pattern=pattern,
                supporting_concepts=meta.get("supporting_concepts", ""),
                difficulty=difficulty,
                link=link,
                notes=notes,
                is_mastered=False,
            )
            RevisionSchedule.objects.get_or_create(problem=problem)
            new_problems_added += 1

            # Log an initial successful attempt
            Attempt.objects.create(
                problem=problem,
                solved_at=solved_datetime,
                time_taken_minutes=25,
                was_successful=True,
                approach_notes=f"Auto-imported from LeetCode Accepted Submission ({solved_datetime.strftime('%Y-%m-%d')}).",
            )
            new_attempts_added += 1
            synced_titles.append(title)
        else:
            # Problem already exists: ensure it has an attempt recorded
            existing_attempt = problem.attempts.filter(
                solved_at__date=solved_datetime.date()
            ).first()
            if not existing_attempt:
                Attempt.objects.create(
                    problem=problem,
                    solved_at=solved_datetime,
                    time_taken_minutes=25,
                    was_successful=True,
                    approach_notes=f"Auto-synced from LeetCode submission on {solved_datetime.strftime('%Y-%m-%d')}.",
                )
                new_attempts_added += 1

    return {
        "success": True,
        "username": profile_data["username"],
        "profile_url": profile_data["profile_url"],
        "ranking": profile_data["ranking"],
        "total_solved": profile_data["total_solved"],
        "easy": profile_data["easy"],
        "medium": profile_data["medium"],
        "hard": profile_data["hard"],
        "topics_solved": profile_data.get("topics_solved", []),
        "topics_count": profile_data.get("topics_count", 0),
        "new_problems_added": new_problems_added,
        "new_attempts_added": new_attempts_added,
        "synced_titles": synced_titles,
        "total_recent_checked": len(profile_data.get("recent_submissions", [])),
    }

