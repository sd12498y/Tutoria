from django.conf.urls import url

from . import views

app_name = 'main'
urlpatterns = [
	# ex: /main/
	url(r'^$', views.login, name='login'),
	url(r'^index/$', views.index, name='index'),
	url(r'^logout/$', views.logout, name='logout'),
	url(r'^register/$', views.register, name='register'),
	url(r'^register/student/$', views.reg_student, name='reg_student'),
	url(r'^wallet/$', views.WalletView.as_view(), name='wallet'),
	url(r'^wallet/addValue/$', views.addValue, name='addValue'),
	url(r'^search/$', views.SearchResultView.as_view(), name='search'),
	url(r'^search/(?P<TutorID>[0-9]+)/$', views.bio, name='bio'),
	url(r'^tutor/(?P<TutorID>[0-9]+)/extimetable/$', views.extimetable, name='extimetable'),
	
	url(r'^booking/(?P<pk>[0-9]+)/cancel$', views.CancelView.as_view(), name='cancel'),
	url(r'^booking/(?P<booking_id>[0-9]+)/confirmcancel$', views.ConfirmCancel, name='confirmCancel'),
	url(r'^bookinghistory/$', views.BookingHistoryView.as_view(), name='bookingHistory'),
	#url(r'^booking/(?P<pk>[0-9]+)/$', views.BookingDetailView.as_view(), name='bookingDetail'),
	url(r'^booking/(?P<pk>[0-9]+)/$', views.BookingDetails, name='bookingDetail'),
	url(r'^search/(?P<TutorID>[0-9]+)/confirmbooking/$', views.confirmBooking, name='confirmBooking'),
]