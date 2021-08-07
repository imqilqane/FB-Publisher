from django.urls import path
from . import views

urlpatterns = [
    path('img/', views.getImg, name='img'),
    path('documentations/', views.docsView, name='doc'),
    path('accounts', views.facebookAccountsView, name='facebookAccounts'),
    path('accounts/delete/<str:pk>/', views.deleteFbAccount, name='delete'),
    path('accounts/edite/<str:pk>/', views.EditFbAccountView, name='edite_fb'),
    path('groups/', views.groupsView, name='groups'),
    path('delete-group/<str:pk>/', views.deleteGroupView, name='del_groups'),
    path('start-compaign/', views.startCopmaignView, name='start_compaign'),
    path('checkaprovment/', views.checkIfGroupsApproved, name='checkaprovment'),
    path('images-galery/', views.imageGaleryView, name='images'),
    path('delete-images/<str:pk>/', views.deleteImg, name='delete_img'),
    path('adcopies/', views.adCopyView, name='adcopies'),
    path('delete-copy/<str:pk>/', views.deleteCopyWrite, name='delete_copy'),
    path('copy-write/', views.addCopyWriteView, name='copy_wirte'),
    path('delete-adcopies/<str:pk>/', views.deleteAdcopy, name='delete_adcopies'),
    path('edit-adcopies/<str:pk>/', views.EditAdCopyView, name='edit_adcopies'),
    path('addniche/', views.addNicheView, name='addniche'),
    path('deleteniche/<str:pk>/', views.deleteNiche, name='deleteniche'),
    path('check-Posted-Approved-And-Change-It-View/', views.checkPostedApprovedAndChangeItView, name='checkPostedApprovedAndChangeIt'),
    
]
