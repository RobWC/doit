function getGroupName() {
    var regex = new RegExp("/group_vars/([a-zA-Z]+)/list"),
        results = regex.exec(location.pathname);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

$('#domainList').change(function(){
  var domainName = $('#domainList').val();
  $.ajax({
    type:"GET",
    url:'/api/1/groups/list?domain=' + domainName,
    success: function(data,textStatus,jqXHR){
      if (textStatus === 'success') {
        $('#groupList').children().remove();
        if (data.length > 0) {
          for (var i = 0; i < data.length; i++) {
            $('#groupList').append('<option value="' + data[i][1] + '">' + data[i][1] + '</option>');
          }
          //select the active domain element
          $('#domainList').val(domainName);
        } else {
            $('#groupList').append('<option value="">None</option>');
        }
      } else {
        console.log('error');
      }
    },
    dataType: 'json'
  });
  //Add group list
});

$("#saveNewGroupVar").click(function () {
  var domainName = $('#domainList').val();
  var groupName = $('#groupList').val();
  var groupVarName = $('#groupVarName').val();
  var groupVarValue = $('#groupVarValue').val();
  //post to api
  $.ajax({
    type:"POST",
    url:'/api/1/group_var/' + groupVarName + '/create?domain=' + domainName + '&group=' + groupName + '&value=' + groupVarValue,
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

$("[id^='deleteGroupVar']").click(function (evtObj) {
  var id = $(evtObj.currentTarget).parent().parent().data('id');
  var groupVarName = $(evtObj.currentTarget).parent().parent().data('id');
  var domainName = getParameterByName('domain');//$(evtObj.currentTarget).parent().parent().data('domain-name');
  var groupName = getGroupName();
  //post to api
  $.ajax({
    type:"DELETE",
    url:'/api/1/group_var/' + groupVarName + '/delete?domain=' + domainName+ '&group=' + groupName,
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

$('#domainList').val(getParameterByName('domain'));