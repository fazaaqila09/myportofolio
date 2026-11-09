from rest_framework.permissions import BasePermission, SAFE_METHODS

EDITOR_GROUP = "Editor"


class IsPortfolioOwnerOrReadOnly(BasePermission):
    """Semua orang boleh membaca; hanya pemilik portofolio (superuser) yang boleh menulis."""

    message = "Only the portfolio owner can change projects."

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_superuser
        )


class IsPortfolioOwnerOrEditorOrReadOnly(BasePermission):
    """Hak akses keempat peran dari Tugas 4, dipakai untuk API Experience.

    - Pengunjung & pengguna biasa : hanya GET/HEAD/OPTIONS.
    - Editor (anggota grup "Editor") : boleh PUT/PATCH, tidak boleh POST/DELETE.
    - Pemilik portofolio (superuser) : boleh semuanya.

    Star tidak diatur di sini; endpoint star memakai IsAuthenticated.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        if request.method in ("PUT", "PATCH"):
            self.message = "Only the portfolio owner or an Editor can edit experience."
            return user.groups.filter(name=EDITOR_GROUP).exists()
        self.message = "Only the portfolio owner can add or delete experience."
        return False
