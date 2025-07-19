$(document).ready(function () {
  var initData = [["","","","","","","","",""]];
  var container = document.getElementById('dataTable');
  
  function customUserGroupRenderer(instance, td, row, col, prop, value, cellProperties) {
    var template = instance.getDataAtRow(row)[1]
    $.ajax({
      type: "GET",
      url: '/api/cm/checkpoint/user-groups?template=' + template,
      success: function (response) {
        cellProperties.chosenOptions.data = response.datalist || [];
      }
    });
    
    var optionsList = cellProperties.chosenOptions.data;
    
    if(typeof optionsList === "undefined" || typeof optionsList.length === "undefined" || optionsList.length === 0 || !optionsList.length) {
      Handsontable.cellTypes.text.renderer(instance, td, row, col, prop, value, cellProperties);
      return td;
    }

    var values = (value + "").split(",");
    value = [];
    for (var index = 0; index < optionsList.length; index++) {
      if (values.indexOf(optionsList[index].id + "") > -1) {
        value.push(optionsList[index].label);
      }
    }
    value = value.join(", ");
    Handsontable.cellTypes.text.renderer(instance, td, row, col, prop, value, cellProperties);
    return td;
  }
  
  var hot = new Handsontable(container, {
    data: initData,
    rowHeaders: true,
    colWidths: '100%',
    rowHeights: 100,
    stretchH: 'all',
    colHeaders: [
      'Username *', 
      'Template', 
      'Is Partner', 
      'Password', 
      'Email',
      'Phone',
      'Expiration Date', 
      'User Groups',
      'Custom Group'
    ],
    manualColumnResize: true,
    columns: [
      {
        type: 'text',
        validator: function(value, callback) {
          if (!value || value.trim() === '') {
            callback(false);
          } else {
            callback(true);
          }
        }
      },
      {
        type: 'autocomplete',
        source(query, process) {
          $.ajax({
            type: "GET",
            url: '/api/cm/checkpoint/user-template',
            success: function (response) {
              if (response.status === 'success') {
                process(response.data);
              } else {
                process([]);
              }
            },
            error: function() {
              process([]);
            }
          })
        },
        strict: false,
        allowInvalid: true
      },
      {
        type: 'autocomplete',
        source: ['false', 'true'],
        strict: true,
        allowInvalid: false
      },
      {
        type: 'text'
      },
      {
        type: 'text',
        validator: function(value, callback) {
          if (!value || value.trim() === '') {
            callback(true);
          } else {
            var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            callback(emailRegex.test(value));
          }
        }
      },
      {
        type: 'text'
      },
      {
        type: 'date',
        dateFormat: 'YYYY-MM-DD',
        correctFormat: true,
        datePickerConfig: {
          firstDay: 0,
          showWeekNumber: true,
          numberOfMonths: 1
        },
        strict: false,
        allowInvalid: true
      },
      {
        renderer: customUserGroupRenderer,
        editor: "chosen",
        chosenOptions: {
          multiple: true,
          data: []
        }
      },
      {
        type: 'text'
      }
    ],
    autoWrapRow: true,
    autoWrapCol: true,
    afterChange: function(changes, source) {
      if (source === 'loadData') {
        return;
      }
      
      if (changes) {
        changes.forEach(function(change) {
          var row = change[0];
          var col = change[1];
          var newValue = change[3];
          
          if (col === 0 && (!newValue || newValue.trim() === '')) {
            hot.setCellMeta(row, col, 'className', 'required-field-error');
          } else if (col === 0 && newValue && newValue.trim() !== '') {
            hot.setCellMeta(row, col, 'className', '');
          }
          
          if (col === 4 && newValue && newValue.trim() !== '') {
            var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(newValue)) {
              hot.setCellMeta(row, col, 'className', 'email-error');
            } else {
              hot.setCellMeta(row, col, 'className', '');
            }
          }
        });
        
        hot.render();
      }
    }
  });

  document.querySelector('#add').addEventListener('click', function () {
    var col = hot.countRows();
    hot.alter('insert_row', col, 1);
  });

  document.querySelector('#submit').addEventListener('click', function () {
    var data = hot.getData();
    var hasErrors = false;
    var errorMessages = [];
    
    for (var i = 0; i < data.length; i++) {
      var row = data[i];
      var rowNum = i + 1;
      
      if (!row.some(cell => cell && cell.toString().trim() !== '')) {
        continue;
      }
      
      if (!row[0] || row[0].trim() === '') {
        errorMessages.push(`Row ${rowNum}: Username is required`);
        hasErrors = true;
      }
      
      if (row[4] && row[4].trim() !== '') {
        var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(row[4])) {
          errorMessages.push(`Row ${rowNum}: Invalid email format`);
          hasErrors = true;
        }
      }
      
      if (row[6] && row[6].trim() !== '') {
        var dateRegex = /^\d{4}-\d{2}-\d{2}$/;
        if (!dateRegex.test(row[6])) {
          errorMessages.push(`Row ${rowNum}: Invalid date format, use YYYY-MM-DD`);
          hasErrors = true;
        }
      }
    }
    
    if (hasErrors) {
      Swal.fire({
        title: 'Validation Error',
        text: errorMessages.join('\n'),
        icon: 'error'
      });
      return;
    }
    
    $('#submit').prop('disabled', true);
    
    var filteredData = data.filter(row => 
      row.some(cell => cell && cell.toString().trim() !== '')
    );
    
    if (filteredData.length === 0) {
      Swal.fire({
        text: 'Please add at least one user',
        icon: 'warning'
      });
      $('#submit').prop('disabled', false);
      return;
    }
    
    console.log('Submitting data:', filteredData);
    
    $.ajax({
      type: "POST",
      url: '/api/cm/checkpoint/create/local-user',
      dataType: "json",
      data: {
        'datalist': filteredData
      },
      success: function (response) {
        if (response.status == 'success') {
          Swal.fire({
            text: response.message,
            icon: "success"
          }).then(function () {
            window.location = '/cm/checkpoint/local-user/list';
          });
        } else {
          Swal.fire({
            text: response.message,
            icon: "error"
          }).then(function () {
            $('#submit').prop('disabled', false);
          });
        }
      },
      error: function (response) {
        Swal.fire({
          text: response.responseJSON.message,
          icon: "error"
        }).then(function () {
          $('#submit').prop('disabled', false);
        });
      }
    });
  });
});