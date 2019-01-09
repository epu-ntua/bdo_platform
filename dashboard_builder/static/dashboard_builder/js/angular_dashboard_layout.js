function pageScroll() {
                $('#main-panel').scrollTop();
            }
        var app = angular.module('myApp', ['gridster']);

        app.config(function ($interpolateProvider) {
            $interpolateProvider.startSymbol('[[');
            $interpolateProvider.endSymbol(']]');
        });

        app.controller('MainCtrl', function ($scope) {
            $scope.counter = "0";
            $scope.tempInnerHtml = "";
            $scope.gridsterOpts = {
                margins: [20, 20],
                swapping: true,
                outerMargin: false,
                pushing: true,
                floating: true,
                columns: 6,
                defaultSizeX: 6,
	            defaultSizeY: 2,
                rowHeight: 200,
                draggable: {
                    enabled: true,
                    handle: '.iframeHeader',
                    start: function (e, ui, $widget) {
                        $('#scroll_down_area').show();
                        $('.wrap1').show();
                    },
                    stop: function (e, ui, $widget) {
                        $('#scroll_down_area').hide();
                        $('.wrap1').hide();
                    }
                },
                resizable: {
                    enabled: true,
                    handles: ['se', 'sw'],
                    start: function (e, ui, $widget) {
                        $('.wrap1').show();
                    }
                    ,
                    stop: function (e, ui, $widget) {
                        $('.wrap1').hide();
                    }
                },
            };

            $scope.standardItems = [];
            function toggleSaveBtn() {
                if ($('#widgetParent li').length > 0 ){
                    $('#save_dashboard_btn').show();
                }
                else{
                    $('#save_dashboard_btn').hide();
                }
            }


            $("#myModal #submit-modal-btn").click(function () {

                var tempid = "#widget" + $scope.counter;

                $scope.standardItems[$scope.standardItems.length - 1].url = document.getElementById("viz_container").querySelector("#viz-iframe").getAttribute('src');

                $(tempid).append('<div class="loadingFrame">' + ' <img src="' + img_source_path + '"/>' +' </div>');
                $('#viz_container iframe').appendTo(tempid);
                toggleSaveBtn();
                $(tempid).find(".loadingFrame").css( "display", "block" );
                $(tempid).find("iframe").on( "load", function(){
                    $(this).siblings(".loadingFrame").css( "display", "none" );
                });

            });



            $("#myModal #submit-note-btn").click(function () {
                var myData = textEditor.getData();
                var tempid = "#widget" + $scope.counter;
                var tempidJs = "widget" + $scope.counter;
                var note_wrapper = "<div class='note_wrapper'>" + myData + " </div>"
                $scope.standardItems[$scope.standardItems.length - 1].noteData = note_wrapper;
                $(String(tempid)+" header").prepend('<input type="submit" id="'+String(tempidJs)+"_edit_btn"+'" class="editnotebtn far fa-edit" data-toggle="modal" data-target="#editNoteModal" value="&#xf044" style="z-index: 4">');
                $(String(tempid)+"_edit_btn").click(function () {
                    widget_open_edit_modal = tempid;
                    widget_edit_id = tempidJs;
                    var edit_data = $(this).parent().parent().find('.note_wrapper').html();
                    textEditNote.setData(edit_data);

                });
                $(tempid).append(note_wrapper);
                $('#save_dashboard_btn').show();
                textEditor.destroy();
                textEditor = null;
                console.log($scope.standardItems);
                $('#viz_config').show();
                $('#model-button-row').show();
                $('#submit-note-btn').hide();
                $('#submit-modal-btn').show();
                var newWidget = document.getElementById(tempidJs);
                for(var i=0 ; i < newWidget.childNodes.length ;i++){
                    if(newWidget.childNodes[i].className == "iframeHeader"){
                        var tempHeader = newWidget.childNodes[i];
                        tempHeader.style.backgroundColor = "white";
                        $(tempHeader).mouseenter(function(){
                        });
                        $(tempHeader).mouseleave(function () {
                            this.style.backgroundColor = "white "
                        });
                        for (var j = 0; j < tempHeader.childNodes.length; j++) {
                            if (tempHeader.childNodes[j].className == "form-group") {
                                tempHeader.childNodes[j].style.display = "none";
                            }
                            if (tempHeader.childNodes[j].className == "deletebtn") {
                                tempHeader.childNodes[j].style.backgroundColor = "white";
                                tempHeader.childNodes[j].style.color = "black";
                            }
                        }
                    }
                }
            });

            $("#submit-note-change-btn").click(function () {
                var edited_note_text = textEditNote.getData();
                $(widget_open_edit_modal).find('.note_wrapper').empty();
                $(widget_open_edit_modal).find('.note_wrapper').append(edited_note_text);
                console.log($scope.standardItems);
                for (var i=0; i<$scope.standardItems.length;i++){
                    if ($scope.standardItems[i].id === widget_edit_id){
                        $scope.standardItems[i].noteData = "<div class='note_wrapper'>" + edited_note_text + " </div>";
                    }
                }
                widget_open_edit_modal = null;
                widget_edit_id = null;
            });
            $("#dismiss-modal-change-btn").click(function () {
                widget_open_edit_modal = null;
                widget_edit_id = null;
            });

            $("#dismiss-modal-btn").click(function () {
                $scope.standardItems.pop();
                $scope.$apply();
                // $('#myModal #viz_container').html('<div class="loadingFrame">' + ' <img src="' + img_source_path + '"/>' + '  </div>');
                $('.viz_item').popover('hide');
                // $('#myModal #viz_config').hide();
                $('#myModal #submit-modal-btn').hide();
            });

            var makeWidget =function (){
                $scope.counter++;
                var tempTitle = "Widget" + $scope.counter;
                $scope.standardItems.push({
                    sizeX: 6,
                    sizeY: 2,
                    row: 0,
                    col: 0,
                    url: "",
                    noteData: "",
                    title: tempTitle,
                    id: "widget" + $scope.counter,
                });
                // setTimeout(function () {
                //     console.log($scope);
                // } ,2000);
                $scope.$apply();
            };

            $('#new_widget_btn').click(makeWidget);
            $('#new_widget_btn').click(function () {
                $('#submit-modal-btn').show();
                $('#modal-tab-data').trigger('click');
            });
            $('#scroll_down_area').mouseenter(function () {
                window.scrollBy(0, 40);
                scrolldelay = setTimeout('pageScroll()', 200);
            });
            $('#scroll_down_area').mouseleave(function () {
                clearTimeout(scrolldelay);
            });
            $scope.finished = function () {
                var tempid = "widget" + $scope.counter;
                $('#viz_container iframe').appendTo(tempid);
            };
            $scope.clear = function () {
                $scope.standardItems = [];
            };
            $scope.removeWidget = function (item) {
                var index = $scope.standardItems.indexOf(item);
                $scope.standardItems.splice(index, 1);
                setTimeout(function() {
                    toggleSaveBtn();
                }, 500);
            };
            angular.element(document).ready(function (e) {
                var prebuiltViz = $('#prebuilt_viz').val();
                if (prebuiltViz != 'None') {
                    makeWidget();
                    var tempid = "#widget" + $scope.counter;
                    $(tempid).append('<div class="loadingFrame">' + ' <img src="' + img_source_path + '"/>' +' </div>');
                    $('#viz_container iframe').appendTo(tempid);
                    $(tempid).find(".loadingFrame").css( "display", "block" );
                    var decodedViz = decodeURIComponent(prebuiltViz);
                    var prebuildIFrameString = "<iframe class='iframe-class' id='viz-iframe' " +
                    "src='" + decodedViz + "' frameborder='0' allowfullscreen='' " +
                    "></iframe>";
                    var prebuildIFrameItem= $.parseHTML(prebuildIFrameString);
                    var helperfunc = function(){
                        $(tempid).append(prebuildIFrameItem[0]);
                        $(tempid).find("iframe").on( "load", function(){
                            $(this).siblings(".loadingFrame").css( "display", "none" );
                        });
                    };
                    setTimeout(helperfunc ,250);
                    $scope.standardItems[$scope.standardItems.length - 1].url = decodedViz;
                    $('#save_dashboard_btn').show();

                }
            });

            $('#save_dashboard_btn').click(function () {
                var postEndpoint = "/dashboards/save/";
                var pk = $('#dashboard_pk').val();
                if (pk !== '') {
                    postEndpoint += pk + '/'
                }
                var post_data_obj = new Object();
                var tempcounter= 0;
                for(var myindex in $scope.standardItems){
                    var tempTitleId= "widgetTitleModel" + myindex.toString();
                    var temparray= [$scope.standardItems[myindex].url , $scope.standardItems[myindex].sizeX.toString() , $scope.standardItems[myindex].sizeY.toString() , $scope.standardItems[myindex].row.toString() , $scope.standardItems[myindex].col.toString() , $scope.standardItems[myindex].title.toString() ,$scope.standardItems[myindex].noteData.toString(),$scope.standardItems[myindex].id.toString()];
                    post_data_obj[String(tempcounter)] = temparray;
                    tempcounter++;
                }
                post_data_obj['title'] = $('#dashboard_title').val();
                post_data_obj['private'] = $('input[name="private"]').is(':checked');
                var post_data = encodeURIComponent(JSON.stringify(post_data_obj));
                $.ajax({
                    "type": "POST",
                    "dataType": "json",
                    "url": postEndpoint,
                    "data": post_data,
                    "beforeSend": function (xhr, settings) {
                        console.log("Before Send");
                        console.log(post_data);
                        $.ajaxSettings.beforeSend(xhr, settings);
                    },
                    "success": function (result) {
                        console.log(result);
                        $('#dashboard_pk').val(result.pk);
                        var id = String(result.pk);
                        window.history.replaceState({}, 'a_title', '/dashboards/create/' + result.pk + '/');
                        // alert('Dashboard saved successfully!');
                        // var message = "Dashboard saved successfully! <br/> You can view it <b><a style='text-decoration: underline;' href='/services/dashboard/"+id+"'/>here</a></b>!"
                        $.notify({
                              icon: "add_alert",
                              message: "Dashboard saved successfully! <br/> You can view it <b><a style='text-decoration: underline' href='/services/dashboard/"+id+"/'>here</a></b>!"

                          },{
                              type: 'success',
                              timer: 4000,
                              placement: {
                                  from: 'top',
                                  align: 'right'
                              }
                          });
                    },
                    error:function(x,e) {
                        var message='Saving dashboard failed!</br>';
                        if (x.status==0) {
                            message+='You are offline!!\n Please Check Your Network.';
                        } else if(x.status==404) {
                            message+='Requested URL not found.';
                        } else if(x.status==500) {
                            message+='Internel Server Error.';
                        } else if(e=='parsererror') {
                            message+='Parsing JSON Request failed.';
                        } else if(e=='timeout'){
                            message+='Request Time out.';
                        } else {
                            message+='Unknow Error.\n'+x.responseText;
                        }
                        $.notify({
                              icon: "add_alert",
                              message: message

                          },{
                              type: 'danger',
                              timer: 4000,
                              placement: {
                                  from: 'top',
                                  align: 'right'
                              }
                          });
                    }
                });
        });
        });