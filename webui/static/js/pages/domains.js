$("#saveNewDomain").click(function () {
  var domainName = $('#domainName').val();
  //post to api
  $.ajax({
    type:"POST",
    url:'/api/1/domain/' + domainName + '/create',
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

$("[id^='deleteDomain']").click(function (evtObj) {
  var id = $(evtObj.currentTarget).parent().parent().data('id');
  var domainName = $(evtObj.currentTarget).parent().parent().data('value');
  //post to api
  $.ajax({
    type:"DELETE",
    url:'/api/1/domain/' + domainName + '/delete',
    complete: function(data,textStatus,jqXHR){
      if (textStatus === 'success') {
        location.reload();
      } else {
        alert('Error adding domain');
        location.reload();
      }
    },
    dataType: 'json'
  });
});