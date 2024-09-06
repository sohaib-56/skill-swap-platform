from django.shortcuts import render, redirect,get_object_or_404
from .models import User, Skilloffer, SkillsNeeded,Post_data,Like,Comment,CommentLike,SwapHistory
from .matching_algorithm import find_all_matches
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
import random, re

# Helper function to check if username is taken
def is_username_taken(username):
    return User.objects.filter(username=username).exists()

# Helper function to authenticate password
def is_password_authenticate(password, cpassword=None):
    if len(password) < 8 or not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
        return False, "Password must be at least 8 characters long and contain both letters and numbers."
    
    if cpassword is not None and password != cpassword:
        return False, "Password & Confirm Password are different."

    return True, ""

# Registration view
def register(request):
    if request.method == 'POST':
        fname = request.POST['fname']
        lname = request.POST['lname']
        dob = request.POST['birthday']
        username = request.POST['username']
        email = request.POST['email']
        phone = request.POST['Phone']
        
        if not fname.isalpha():
            messages.error(request, "First name should only contain letters.")
            return redirect('register')

        if not lname.isalpha():
            messages.error(request, "Last name should only contain letters.")
            return redirect('register')

        # Check if the username is already taken
        if is_username_taken(username):
            messages.error(request, "Username is already taken.")
            return redirect('register')

        # Check if the email is already registered
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect('register')

        # Create and save the user data
        user = User.objects.create(
            first_name=fname, last_name=lname, dob=dob, username=username, email=email, phone=phone
        )
        
        request.session['user_id'] = user.id
        
        # Generate and send OTP
        otp = random.randint(100000, 999999)
        request.session['otp'] = otp
        print(f"OTP : {otp}")  # In a real application, send OTP via email
        
        messages.success(request, "OTP is sent to the given email.")
        return redirect('validate')

    return render(request, 'register.html')

# Verify email view
def verify_email(request):
    if request.method == 'POST':
        email = request.POST['email']
        otp = random.randint(100000, 999999)
        if User.objects.filter(email=email).exists():
            request.session['otp'] = otp
            request.session['semail'] = email
            print(f"Email : {email} OTP : {otp}")
            messages.success(request, "Email exists, and OTP is sent.")
            return redirect('validate')
        else:
            messages.error(request, "Email not found.")
            return redirect('verify_email')
    return render(request, 'verify_email.html')

# Validate OTP view
def validate(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('OTP')
        sent_otp = request.session.get('otp')
        user_id = request.session.get('user_id')

        if int(sent_otp) == int(entered_otp):
            # Mark email as verified in the user's data
            user = User.objects.get(id=user_id)
            user.email_verified = True  
            user.save()

            # Clear OTP from session after successful verification
            request.session.pop('otp', None)

            messages.success(request, "OTP verified successfully!")
            return redirect('Set_password')
        else:
            messages.error(request, "Invalid OTP!")
            return redirect('register')

    return render(request, 'validate.html')

# Set password view
def Set_password(request):
    user_id = request.session.get('user_id')

    # Check if the email is verified
    if not user_id:
        messages.error(request, "Unauthorized access. Please complete the verification process.")
        return redirect('register')
    
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        password = request.POST['password']
        cpassword = request.POST['cpassword']

        is_valid, message = is_password_authenticate(password, cpassword)
        if not is_valid:
            messages.error(request, message)
            return redirect('Set_password')
        user.password = password  
        user.save()

        messages.success(request, 'Password set successfully.')
        return redirect('Skills_offer')

    return render(request, 'Set_password.html')

# Skills offer view
def Skills_offer(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    if not user.email_verified:
        messages.error(request, "Please verify your email before proceeding.")
        return redirect('register')

    if request.method == 'POST':
        skills_offered = request.POST.getlist('skills_offered[]')
        experience_levels = request.POST.getlist('experience_level_offered[]')

        valid_entries = []  

        for skill, level in zip(skills_offered, experience_levels):
            if skill.strip() and level: 
                if skill.isalpha(): 
                    valid_entries.append((skill, level))
                else:
                    messages.error(request, "Each skill should only contain letters.")
                    return redirect('Skills_offer')
            else:
                continue
        for skill, level in valid_entries:
            Skilloffer.objects.create(
                user=user, skill_offered=skill, experience_level_offered=level
            )

        messages.success(request, "Skills offered have been successfully saved.")
        return redirect('Skills_need')

    return render(request, 'Skills_offer.html')


# Skills need view
def Skills_need(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)

    if not user.email_verified:
        messages.error(request, "Please verify your email before proceeding.")
        return redirect('register')

    if request.method == 'POST':
        skills_needed = request.POST.getlist('skills_needed[]')
        experience_levels = request.POST.getlist('experience_level_needed[]')
        priorities = request.POST.getlist('priorities[]') 

        valid_entries = [] 

        for skill, level, priority in zip(skills_needed, experience_levels, priorities):
            if skill.strip() and level and priority: 
                if skill.isalpha():  
                    valid_entries.append((skill, level, priority))
                else:
                    messages.error(request, "Each skill should only contain letters.")
                    return redirect('Skills_need')
            else:
                continue
        for skill, level, priority in valid_entries:
            SkillsNeeded.objects.create(
                user=user, skill=skill, experience_level=level, priority=int(priority)
            )
        
        messages.success(request, "Skills needed have been successfully saved.")
        return redirect('login')

    return render(request, 'skills_need.html')

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', None)
        pass1 = request.POST.get('password', None)

        if not username or not pass1:
            messages.error(request, 'Username and Password are required')
            return redirect('login')

        try:
            user = User.objects.get(username=username, password=pass1)
            if user:
                request.session['user_id'] = user.id
                messages.success(request, "Logged in successfully.")
                return redirect('home')
            else:
                messages.error(request, 'Username or Password is incorrect')
        except User.DoesNotExist:
            messages.error(request, 'User does not exits')
            return redirect('login')

    return render(request, 'login.html')

#logout view
@login_required(login_url='login')
def logout(request):
    try:
        auth_logout(request)
        messages.success(request, 'Logout successful')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
    return redirect('login')

#home view
def home(request):
    try:
        user_id = request.session.get('user_id')
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request,'Userdata not found')
        return redirect('register')
    posts = Post_data.objects.all().order_by('-time_posted')
    liked_posts = Like.objects.filter(user = user).values_list('post_id', flat=True)
    comments = Comment.objects.all().order_by('-created_at')
    liked_comments = CommentLike.objects.filter(user = user).values_list('comment_id', flat=True)
    context = {
        'posts': posts,
        'liked_posts': liked_posts,
        'user' : user,
        'comments': comments,
        'liked_comments': liked_comments,
    }

    if request.method == 'POST':
        post_content = request.POST.get('post')
        if post_content:
            try:
                user = User.objects.get(id=user_id)
                post = Post_data(mypost=post_content, user=user)
                post.save()
                messages.success(request, 'Your post is saved.')
            except Exception as e:
                messages.error(request, f'Error saving post: {str(e)}')
        else:
            messages.error(request, 'Post content cannot be empty.')

        return redirect('home')

    return render(request, 'home.html', context)


#Like view 
def like_post(request, post_id):
    post = get_object_or_404(Post_data, id=post_id)
    user = User.objects.get(id=request.session.get('user_id'))
    like = Like.objects.filter(post=post, user=user)
    if like:
        like.delete()
        messages.success(request, 'You have unliked post')
    else:
        Like.objects.create(post=post, user=user)
        messages.success(request, 'You liked this post.')
    return redirect('home')

#settings

def settings(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)

    return render(request,'settings.html', {'username':user.username})

#change password
@login_required(login_url='login')
def change_password(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id) 
    if request.method == 'POST':
        current_password = request.POST['current_password'] 
        new_password = request.POST['new_password'] 
        confirm = request.POST['confirm_password']
        if current_password != user.password:
            messages.error(request,'You have entered wrong current password')
            return redirect('change_password')
        is_valid, message = is_password_authenticate(new_password, confirm)
        if not is_valid:
            messages.error(request, message)
            return redirect('change_password')
        user.password = new_password
        user.save()
        messages.success(request,'Password changed')
        return redirect('settings')
    return render(request,'Update_password.html',{'user':user})

#update profile
def profile(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        first_name = request.POST['fname']
        last_name = request.POST['lname']
        email = request.POST['email']
        if not first_name.isalpha():
            messages.error(request, "First name should only contain letters.")
            return redirect('register')

        if not last_name.isalpha():
            messages.error(request, "Last name should only contain letters.")
            return redirect('register')
        user = User.objects.update(
            first_name=first_name, last_name=last_name,  email=email, 
        )
        messages.success(request,'Profile updated successfully')
        return redirect('home')
    return render(request,'profile.html',{'user':user})

#update skills 
def skills_update(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    user_data = User.objects.get(username=user.username)
    
    # Fetch existing skills
    existing_skills_offered = Skilloffer.objects.filter(user=user_data)
    existing_skills_needed = SkillsNeeded.objects.filter(user=user_data)
    
    if request.method == 'POST':
        # Clear old skills
        existing_skills_offered.delete()
        existing_skills_needed.delete()

        # Handle offered skills
        offered_skills = request.POST.getlist('skills_offered[]')
        offered_experience_levels = request.POST.getlist('experience_level_offered[]')
  
        for skill, level in zip(offered_skills, offered_experience_levels):
            if skill and level:  # Check if skill and level are provided
                Skilloffer.objects.create(user=user_data, skill_offered=skill, experience_level_offered=level)

        # Handle needed skills
        needed_skills = request.POST.getlist('skills_needed[]')
        needed_experience_levels = request.POST.getlist('experience_level_needed[]')
        priorities = request.POST.getlist('priorities[]')
        
        for skill, level, priority in zip(needed_skills, needed_experience_levels, priorities):
            if skill and level and priority:  # Check if skill, level, and priority are provided
                SkillsNeeded.objects.create(user=user_data, skill=skill, experience_level=level, priority=priority)
        
        messages.success(request, 'Skills updated successfully.')
        return redirect('settings')

    context = {
        'skills_offered': existing_skills_offered,
        'skills_needed': existing_skills_needed,
        'user': user,
    }
    return render(request, 'skills_update.html', context)


#comment view
def comment(request, post_id):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        post = get_object_or_404(Post_data, id=post_id)
        comment = request.POST.get('comment')
        if comment:
            Comment.objects.create(post=post, user=user, comment=comment)
            return redirect('home')
        

#commentlike view
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    user = User.objects.get(id=request.session.get('user_id'))
    like = CommentLike.objects.filter(comment=comment, user=user)
    if like:
        like.delete()
        messages.success(request, 'You have unliked comment')
    else:
        CommentLike.objects.create(comment=comment, user=user)
        messages.success(request, 'You liked this comment')
    return redirect('home')

#match view
# @login_required(login_url='login')
def match_view(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)  
    if not user.email_verified:
        messages.error(request, "Please verify your email before finding matches.")
        return redirect('home')
    
    # Find match chains using BFS for all users
    match_results = find_all_matches(max_depth=3)
    
    # Enhance chains with user details and reputation for the current user
    enhanced_chains = []
    if user_id in match_results:
        match_chains = match_results[user_id]
        for chain in match_chains:
            chain_details = []
            for matched_user in chain:
                chain_details.append({
                    'username': matched_user.username,
                    'first_name': matched_user.first_name,
                    'last_name': matched_user.last_name,
                    'reputation': matched_user.reputation,
                    'profile_url': f'/profile/{matched_user.id}/'
                })
            enhanced_chains.append(chain_details)
    
    context = {
        'match_chains': enhanced_chains,
        'user': user,
    }
    
    return render(request, 'match.html', context)


def profile_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    skillsneed = get_object_or_404(SkillsNeeded,id=user_id)
    skillsoffer = get_object_or_404(Skilloffer,id=user_id)
    context = {'user': user,'skillsneed':skillsneed,'skillsoffer':skillsoffer,}
    return render(request, 'userprofile.html', context)


def connect_view(request):
    pass


def Userdashboard(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)

    # if not user.is_authenticated:
    #     return redirect('login')  # Redirect to login page if user is not authenticated

    # Fetch user-specific data
    try:
        user = User.objects.get(username=user.username)
        skillsoffer = Skilloffer.objects.filter(user=user)
        skillsneed = SkillsNeeded.objects.filter(user=user)
        match_count = ...  # Fetch match suggestions count
        swap_history_count = SwapHistory.objects.filter(user=user).count()
        upcoming_sessions_count = ...  # Fetch count of upcoming sessions
        recent_activity = ...  # Fetch recent activity
        skill_in_progress = ...  # Fetch skill improvement progress
    except User.DoesNotExist:
        # Handle case where user data does not exist
        user = None
        skillsoffer = None
        skillsneed = None
        match_count = 0
        swap_history_count = 0
        upcoming_sessions_count = 0
        recent_activity = "No recent activity"
        skill_in_progress = "No progress tracked"

    context = {
        'user': user,
        'skillsoffer': skillsoffer,
        'skillsneed': skillsneed,
        'match_count': match_count,
        'swap_history_count': swap_history_count,
        'upcoming_sessions_count': upcoming_sessions_count,
        'recent_activity': recent_activity,
        'skill_in_progress': skill_in_progress,
    }

    return render(request, 'Userdashboard.html', context)
