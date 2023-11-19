<div class="content-box">
    <table id="grid-data" class="table table-condensed table-striped" data-editDialog="DialogNetScan">
        <thead>
            <tr>
                <th data-column-id="Name" data-formatter="multiline" data-width="12em" >Name</th>
                <th data-column-id="Device" data-width="10em">Device</th>
                <th data-column-id="IPV4" data-width="5em" data-formatter="multiline" data-order="asc">IPv4</th>
                <th data-column-id="IPV6" data-width="12em" data-formatter="multiline">IPv6</th>
                <th data-column-id="MAC" data-width="9em">MAC Address</th>
                <th data-column-id="Last" data-width="7em" data-formatter="since">Last Seen</th>
               <th data-column-id="commands" data-width="3em" data-formatter="commands" data-sortable="false"></th>
            </tr>
        </thead>
        <tbody>
        </tbody>
    </table>        
</div>

{{ partial("layout_partials/base_dialog",['fields':formDialogNetScan,'id':'DialogNetScan','label':'Edit Net Scan'])}}

<script>
function timeSince(date) {
  if (date.getFullYear() < 2000) return "";

  var seconds = Math.floor((new Date() - date) / 1000);

  var interval = seconds / 31536000;
  if (interval > 1) {
    return Math.floor(interval) + " years";
  }
  interval = seconds / 2592000;
  if (interval > 1) {
    return Math.floor(interval) + " months";
  }
  interval = seconds / 86400;
  if (interval > 1) {
    return Math.floor(interval) + " days";
  }
  interval = seconds / 3600;
  if (interval > 1) {
    return Math.floor(interval) + " hours";
  }
  interval = seconds / 60;
  if (interval > 1) {
    return Math.floor(interval) + " minutes";
  }
  return Math.floor(seconds) + " seconds";
}

    $(document).ready(function() {
        $("#grid-data").UIBootgrid({
            search:'/api/netscan/service/search/',
                get:'/api/netscan/service/getName/',
                set:'/api/netscan/service/setName/',
            options: {
                 rowSelect: false,
                 multiSelect: false,
                 selection: false,
                 formatters: {
                     "multiline": function (column, row) {
									 if (row[column.id] == "~") return "";
                           return row[column.id].replaceAll('\\','<br />');
                      },
                      "since": function(column, row) {
                           return timeSince(new Date(row[column.id]));
                      },
                      "commands": function (column, row) {
                            return '<button type="button" class="btn btn-xs btn-default command-edit bootgrid-tooltip" data-row-id="' + row.MAC + '"><span class="fa fa-fw fa-pencil"></span></button>';
                      }
						},
              }
           });
    });
</script>

