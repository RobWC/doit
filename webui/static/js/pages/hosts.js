$("#saveNewHost").click(function () {
  var domainName = $('#domainList').val();
  var hostName = $('#hostName').val();
  //post to api
  $.ajax({
    type:"POST",
    url:'/api/1/host/' + hostName + '/create?domain=' + domainName,
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

$("[id^='deleteHost']").click(function (evtObj) {
  var id = $(evtObj.currentTarget).parent().parent().data('id');
  var hostName = $(evtObj.currentTarget).parent().parent().data('value');
  var domainName = $(evtObj.currentTarget).parent().parent().data('domain-name');
  //post to api
  $.ajax({
    type:"DELETE",
    url:'/api/1/host/' + hostName + '/delete?domain=' + domainName,
    complete: function(data,textStatus,jqXHR){
      if (textStatus === 'success') {
        location.reload();
      } else {
        alert('Error adding host');
        location.reload();
      }
    },
    dataType: 'json'
  });
});