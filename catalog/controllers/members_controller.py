from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib.auth import get_user_model

from catalog.entities import CatalogActivity, CatalogInvite, CatalogMember

User = get_user_model()


def get_catalog_member(request):
    catalog = request.user.active_catalog
    member = CatalogMember.objects.filter(
        catalog=catalog,
        user=request.user
    ).first()
    return catalog, member


# -----------------------------------
# LIST MEMBERS
# -----------------------------------

@require_POST
def api_members_list(request):

    catalog, member = get_catalog_member(request)

    if not member:
        return JsonResponse({"error": "access_denied"}, status=403)

    members = CatalogMember.objects.filter(
        catalog=catalog
    ).select_related("user")

    return JsonResponse({
        "members": [
            {
                "id": m.id,
                "name": m.user.display_name,
                "phone": m.user.phone,  # شماره تماس به جای ایمیل
                "role": m.role
            }
            for m in members
        ]
    })


# -----------------------------------
# INVITE MEMBER
# -----------------------------------

@require_POST
def api_member_invite(request):

    catalog, member = get_catalog_member(request)

    if not member or not member.has_permission("catalog", "manage_members"):
        return JsonResponse({"error": "access_denied"}, status=403)

    phone = request.POST.get("phone")
    role = request.POST.get("role")

    if not phone:
        return JsonResponse({"error": "phone_required"}, status=400)

    # جلوگیری از دعوت تکراری بر اساس شماره تماس
    if CatalogInvite.objects.filter(catalog=catalog, phone=phone).exists():
        return JsonResponse({"error": "invite_exists"}, status=400)

    invite = CatalogInvite.objects.create(
        catalog=catalog,
        phone=phone,
        role=role,
    )

    CatalogActivity.objects.create(
        catalog=catalog,
        actor=request.user,
        action="invite_member",
        meta={"phone": phone, "role": role}
    )

    return JsonResponse({
        "status": "ok",
        "invite_id": invite.id
    })


# -----------------------------------
# UPDATE MEMBER ROLE
# -----------------------------------

@require_POST
def api_member_update(request, member_id):

    catalog, actor = get_catalog_member(request)

    if not actor or not actor.has_permission("catalog", "manage_members"):
        return JsonResponse({"error": "access_denied"}, status=403)

    try:
        member = CatalogMember.objects.get(
            id=member_id,
            catalog=catalog
        )
    except CatalogMember.DoesNotExist:
        return JsonResponse({"error": "member_not_found"}, status=404)

    role = request.POST.get("role")

    if member.role == CatalogMember.Role.OWNER:
        return JsonResponse({"error": "cannot_modify_owner"}, status=400)

    member.role = role
    member.save(update_fields=["role"])

    CatalogActivity.objects.create(
        catalog=catalog,
        actor=request.user,
        action="update_member_role",
        meta={
            "phone": member.user.phone,
            "role": role
        }
    )

    return JsonResponse({"status": "updated"})


# -----------------------------------
# DELETE MEMBER
# -----------------------------------

@require_POST
def api_member_delete(request, member_id):

    catalog, actor = get_catalog_member(request)

    if not actor or not actor.has_permission("catalog", "manage_members"):
        return JsonResponse({"error": "access_denied"}, status=403)

    try:
        member = CatalogMember.objects.select_related("user").get(
            id=member_id,
            catalog=catalog
        )
    except CatalogMember.DoesNotExist:
        return JsonResponse({"error": "member_not_found"}, status=404)

    if member.role == CatalogMember.Role.OWNER:
        return JsonResponse({"error": "cannot_delete_owner"}, status=400)

    phone = member.user.phone

    member.delete()

    CatalogActivity.objects.create(
        catalog=catalog,
        actor=request.user,
        action="remove_member",
        meta={"phone": phone}
    )

    return JsonResponse({"status": "deleted"})


# -----------------------------------
# RESEND INVITE
# -----------------------------------

@require_POST
def api_invite_resend(request, token):

    catalog, member = get_catalog_member(request)

    if not member or not member.has_permission("catalog", "manage_members"):
        return JsonResponse({"error": "access_denied"}, status=403)

    try:
        invite = CatalogInvite.objects.get(
            token=token,
            catalog=catalog
        )
    except CatalogInvite.DoesNotExist:
        return JsonResponse({"error": "invite_not_found"}, status=404)

    invite.expires_at = timezone.now() + timezone.timedelta(days=7)
    invite.save(update_fields=["expires_at"])

    CatalogActivity.objects.create(
        catalog=catalog,
        actor=request.user,
        action="resend_invite",
        meta={"phone": invite.phone}
    )

    return JsonResponse({"status": "resent"})


# -----------------------------------
# CANCEL INVITE
# -----------------------------------

@require_POST
def api_invite_cancel(request, token):

    catalog, member = get_catalog_member(request)

    if not member or not member.has_permission("catalog", "manage_members"):
        return JsonResponse({"error": "access_denied"}, status=403)

    try:
        invite = CatalogInvite.objects.get(
            token=token,
            catalog=catalog
        )
    except CatalogInvite.DoesNotExist:
        return JsonResponse({"error": "invite_not_found"}, status=404)

    phone = invite.phone

    invite.delete()

    CatalogActivity.objects.create(
        catalog=catalog,
        actor=request.user,
        action="cancel_invite",
        meta={"phone": phone}
    )

    return JsonResponse({"status": "canceled"})
