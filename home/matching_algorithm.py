from collections import deque
from .models import User, Skilloffer, SkillsNeeded

def build_bidirectional_graph():
    """
    Builds a bidirectional graph where an edge exists between User A and User B
    only if User A offers a skill that User B needs AND User B offers a skill that User A needs.
    """
    graph = {}
    users = User.objects.all()
    
    # Pre-fetch related skills to optimize database queries
    user_offers = Skilloffer.objects.select_related('user').all()
    user_needs = SkillsNeeded.objects.select_related('user').all()
    
    # Create dictionaries for quick lookup
    offers_dict = {}
    needs_dict = {}
    
    for offer in user_offers:
        offers_dict.setdefault(offer.user.id, set()).add(offer.skill_offered.lower())
    
    for need in user_needs:
        needs_dict.setdefault(need.user.id, set()).add(need.skill.lower())
    
    # Build the adjacency list with mutual exchange criteria
    for user in users:
        graph[user.id] = set()
        user_offer_skills = offers_dict.get(user.id, set())
        user_needs_skills = needs_dict.get(user.id, set())
        
        for other_user in users:
            if other_user.id == user.id:
                continue
            other_user_offer_skills = offers_dict.get(other_user.id, set())
            other_user_needs_skills = needs_dict.get(other_user.id, set())
            
            # Check mutual skill exchange
            if (user_offer_skills.intersection(other_user_needs_skills) and
                other_user_offer_skills.intersection(user_needs_skills)):
                graph[user.id].add(other_user.id)
    
    return graph

def bfs_bidirectional(graph, start_user_id, max_depth=3):
    """
    Performs BFS on the bidirectional graph to find chains of users up to a specified depth.
    Returns a list of paths, where each path is a list of user IDs.
    """
    visited = set()
    queue = deque([[start_user_id]])
    paths = []

    while queue:
        path = queue.popleft()
        current = path[-1]

        if len(path) > max_depth:
            continue

        for neighbor in graph.get(current, []):
            if neighbor == start_user_id:
                continue  # Avoid cycles back to the start
            if neighbor not in path:  # Avoid revisiting nodes in the current path
                new_path = list(path)
                new_path.append(neighbor)
                paths.append(new_path)
                queue.append(new_path)
                visited.add(neighbor)
    
    return paths

def find_all_matches(max_depth=3):
    """
    Finds matching chains for all users using a bidirectional graph.
    Returns a dictionary where the key is the user ID and the value is a list of match chains.
    """
    graph = build_bidirectional_graph()
    all_matches = {}

    for user in User.objects.all():
        start_user_id = user.id
        paths = bfs_bidirectional(graph, start_user_id, max_depth)
        
        # Convert user IDs back to User objects
        match_chains = []
        for path in paths:
            chain = User.objects.filter(id__in=path).order_by('id')
            chain_users = list(chain)
            match_chains.append(chain_users)
        
        all_matches[user.id] = match_chains
    
    return all_matches
