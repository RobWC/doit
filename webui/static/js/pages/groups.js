$("#saveNewGroup").click(function () {
  var domainName = $('#domainList').val();
  var groupName = $('#groupName').val();
  //post to api
  $.ajax({
    type:"POST",
    url:'/api/1/group/' + groupName + '/create?domain=' + domainName,
    complete: function(data,textStatus,jqXHR){
      if (textStatus === 'success') {
        location.reload();
      } else {
        $('#pageModal').modal('hide');
        alert('Error adding domain');
      }
    },
    dataType: 'json'
  });
});

$("[id^='deleteGroup']").click(function (evtObj) {
  var id = $(evtObj.currentTarget).parent().parent().data('id');
  var groupName = $(evtObj.currentTarget).parent().parent().data('value');
  var domainName = $(evtObj.currentTarget).parent().parent().data('domain-name');
  //post to api
  $.ajax({
    type:"DELETE",
    url:'/api/1/group/' + groupName + '/delete?domain=' + domainName,
    complete: function(data,textStatus,jqXHR){
      if (textStatus === 'success') {
        location.reload();
      } else {
        alert('Error deleting group');
        location.reload();
      }
    },
    dataType: 'json'
  });
});