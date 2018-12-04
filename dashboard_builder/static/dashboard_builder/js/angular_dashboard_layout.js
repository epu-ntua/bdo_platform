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
                $(tempid).append(note_wrapper);
                $('#save_dashboard_btn').show();
                textEditor.destroy();
                textEditor = null;
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
            $("#dismiss-modal-btn").click(function () {
                $scope.standardItems.pop();
                $scope.$apply();
                $('#myModal #viz_container').html('<div class="loadingFrame">' + ' <img src="' + img_source_path + '"/>' + '  </div>');
                $('.viz_item').popover('hide');
                $('#myModal #viz_config').hide();
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
                    title: tempTitle
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
                    var decodedViz = decodeURIComponent(prebuiltViz);
                    var prebuildIFrameString = "<iframe class='iframe-class' id='viz-iframe' " +
                    "src='" + decodedViz + "' frameborder='0' allowfullscreen='' " +
                    "></iframe>";
                    var prebuildIFrameItem= $.parseHTML(prebuildIFrameString);
                    var helperfunc = function(){
                        $(tempid).append(prebuildIFrameItem[0]);
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
                    var temparray= [$scope.standardItems[myindex].url , $scope.standardItems[myindex].sizeX.toString() , $scope.standardItems[myindex].sizeY.toString() , $scope.standardItems[myindex].row.toString() , $scope.standardItems[myindex].col.toString() , $scope.standardItems[myindex].title.toString() ,$scope.standardItems[myindex].noteData.toString()];
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
                        window.history.replaceState({}, 'a_title', '/dashboards/create/' + result.pk + '/');
                        alert('Dashboard saved successfully!');
                    },
                    error:function(x,e) {
                        if (x.status==0) {
                            alert('You are offline!!\n Please Check Your Network.');
                        } else if(x.status==404) {
                            alert('Requested URL not found.');
                        } else if(x.status==500) {
                            alert('Internel Server Error.');
                        } else if(e=='parsererror') {
                            alert('Error.\nParsing JSON Request failed.');
                        } else if(e=='timeout'){
                            alert('Request Time out.');
                        } else {
                            alert('Unknow Error.\n'+x.responseText);
                        }
                    }
                });
        });
        });