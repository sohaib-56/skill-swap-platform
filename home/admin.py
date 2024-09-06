from django.contrib import admin
from.models import User,Skilloffer,SkillsNeeded,Post_data,Like,Comment,CommentLike,SwapHistory,MatchSuggestion
# Register your models here.
admin.site.register(User)
admin.site.register(Skilloffer)
admin.site.register(SkillsNeeded)
admin.site.register(Post_data)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(CommentLike)
admin.site.register(SwapHistory)
admin.site.register(MatchSuggestion)