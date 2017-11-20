function custom_fill_notification_list(data) {
			    var menu = document.getElementById(notify_menu_id);
			    if (menu) {
			        var content = [];
			        menu.innerHTML = data.unread_list.map(function (item) {
			            var message = "";
			            /*
			            if(typeof item.actor !== 'undefined'){
			                message = item.actor;
			            }*/
			            if(typeof item.verb !== 'undefined'){
			                message = message + " " + item.verb;
			            }
			            if(typeof item.target !== 'undefined'){
			                message = message + " " + item.target;
			            }
			            if(typeof item.timestamp !== 'undefined'){
			                message = message + "</br> " + item.timestamp;
			            }
			            return '<li><a href="#">' + message + '</a></li>';
			        }).join(' <li role="separator" class="divider"></li>')
			    }
}
$(document).ready(function(){
    $('.dropdown').on('hidden.bs.dropdown', function(){
        				var r = new XMLHttpRequest();
						
						r.onreadystatechange = function() {
    						if (this.readyState == 4 && this.status == 200) {
       						// Action to be performed when the document is read;
                					return;
    						}
						};
                		r.open("GET", "/inbox/notifications/api/unread_list/?mark_as_read=true", true);
        				r.send();
    });
});