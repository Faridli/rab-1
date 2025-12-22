from django.contrib import admin
from .models import (
    ForceMember,
    PresentAddress,
    PermanentAddress,
    # Ro,
    MiRoomVisit,
    Duty,
    Mt,
    TrgBr,
    # MemberPosting
)

admin.site.register(ForceMember)
admin.site.register(PresentAddress)
admin.site.register(PermanentAddress)
# admin.site.register(Ro)
admin.site.register(MiRoomVisit)
admin.site.register(Duty)
admin.site.register(Mt)
admin.site.register(TrgBr)
# admin.site.register(MemberPosting)
