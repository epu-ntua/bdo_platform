/* usage:
    paginate(mode) :
        creates the paging list for the data.
        mode { open / closed } for which data should make the pagination

    call( mode, title, sector, paginate ):
        function for filling list of data.
        mode { user, all, search } refers to which data should the list include
        title is the title which the user searches - associated with search mode
        sector is in which page of results the user is
        paginate { true / false } if pagination is needed eg. when going from 'all' to 'user'

    populate2(div, data, sector, perpage):
        fill the list with data.
        div refers to the element that will show the data
        data is the list of elements to be displayed
        sector is the current page in the paging where the user is so that it will display the right range of data
        perpage is the amount of entries per page.

*/

var sectionopen = 0;
var sectionclosed = 0;
var hasmoreopen = false;
var hasmoreclosed = false;
var title = '';

function initialize(){
    sectionopen = 0;
    sectionclosed = 0;
    hasmoreopen = false;
    hasmoreclosed = false;
}

function isactive(element){
    element = '#' + element;
    return $(element).hasClass("active");
}

$(document).ready(function() {

    call("all", '', 1, true);
    //paginate("open");


    $('#all').click(function(e){
        if( !isactive('all') ){
            initialize();
            title = '';
            call('all', '', 1, true);
            document.getElementById("all").setAttribute("class", "btn btn-default active");
            document.getElementById("user").setAttribute("class", "btn btn-default");
            document.getElementById("openus").setAttribute("class", "active");
            document.getElementById("closedus").setAttribute("class", "");
        }
    });
    $('#user').click(function(e){
        if( !isactive('user') ) {
            initialize();
            title = '';
            call('user', '', 1, true);
            document.getElementById("user").setAttribute("class", "btn btn-default active");
            document.getElementById("all").setAttribute("class", "btn btn-default");
            document.getElementById("openus").setAttribute("class", "active");
            document.getElementById("closedus").setAttribute("class", "");
        }
    });
    $('#search').click(function(e){
        initialize();
        title = document.getElementById('title').value;
        call('search', title, 1, true);
        //paginate("open");
        document.getElementById("user").setAttribute("class", "btn btn-default");
        document.getElementById("all").setAttribute("class", "btn btn-default");
        document.getElementById("openus").setAttribute("class", "active");
        document.getElementById("closedus").setAttribute("class", "");
        document.getElementById("openn").setAttribute("class", "tab-pane fade in active");
        document.getElementById("closedd").setAttribute("class", "tab-pane fade");
    });
    $("#title").keyup(function(event){
        if (event.keyCode === 13){                                      // when pressing enter also
            $("#search").click();
        }
    });
    $("#opentab").click(function(e){
       paginate("open");
    });
    $("#closedtab").click(function(e){
       paginate("closed");
    });
    $("#opentabl").click(function(e){
        if( !isactive('openus') ) {
            paginate("open");
            var mode;
            if (isactive('all')) {
                mode = "all";
            }
            else if (isactive('user')) {
                mode = "user";
            }
            else {
                mode = "search";
            }
            call(mode, title, 1, false);
            sectionclosed = 0;
        }
    });
    $("#closedtabl").click(function(e){
        if( !isactive('closedus') ) {
            paginate("closed");
            var mode;
            if (isactive('all')) {
                mode = "all";
            }
            else if (isactive('user')) {
                mode = "user";
            }
            else {
                mode = "search";
            }
            call(mode, title, 1, false);
            sectionopen = 0;
        }
    });
    $('#paging').on('click', 'a', function(e){
        e.preventDefault();
        var sector = $(this);
        var parent = sector.parent().attr('id');
        var mode, tab, hasmore, section;

        if ( parent != 'next' && parent != 'previous' ){
            sector.parent().siblings().removeClass('active').end().addClass('active');
        }
        else{
            if( isactive('openus') ){
                tab = 'open';
                hasmore = hasmoreopen;
                section = sectionopen;
            }
            else{
                tab = 'closed';
                hasmore = hasmoreclosed;
                section = sectionclosed;
            }
            if( parent == 'previous' ){
                if(section == 0){
                    sector.parent().siblings().removeClass('active');
                    sector.parent().next().addClass('active');
                    sector = sector.parent().next().children();
                }
                else{
                    if(tab == 'open'){
                        sectionopen -=1;
                        paginate('open');
                    }
                    else{
                        sectionclosed -=1;
                        paginate('closed');
                    }
                    sector = $('#next').prev().children();
                    sector.parent().siblings().removeClass('active');
                    sector.parent().addClass('active');
                }
            }
            else{
                if(!hasmore){
                    sector.parent().siblings().removeClass('active');
                    sector.parent().prev().addClass('active');
                    sector = sector.parent().prev().children();
                }
                else{
                    if(tab == 'open'){
                        sectionopen +=1;
                        paginate('open');
                    }
                    else{
                        sectionclosed +=1;
                        paginate('closed');
                    }
                    sector = $('#previous').next().children();
                    //sector.parent().siblings().removeClass('active');                 when paging active is always the first
                    //sector.parent().addClass('active');
                }
            }
        }
        console.log(" click on "+sector.text());
        console.log(sector.parent().attr('id'));
        if( isactive('all') ){
            mode = "all";
        }
        else if( isactive('user') ){
            mode = "user";
        }
        else{
            mode = "search";
        }
        call(mode, title, sector.text(), false);
    });
});

function call(mode, title, sector, call_for_paginate){
    $.ajax({
        url: 'users/',
        datatype: 'json',
        type: 'GET',
        data: {'mode': mode, 'title': title},
        success: function (data) {
            var rows, i;

            var open = data.open;
            var closed = data.closed;
            var sum = data.sum;


            var opdiv = document.getElementById('openn');
            var cldiv = document.getElementById('closedd');

            opdiv.innerHTML = "";
            cldiv.innerHTML = "";
            /*
            var optable = document.getElementById('otbody');
            var cltable = document.getElementById('ctbody');


            rows = optable.rows.length;
            if( rows > 0 ){
                for(i=rows-1; i>=0; i--){
                    optable.deleteRow(i);
                }
            }
            rows = cltable.rows.length;
            if( rows > 0 ){
                for(i=rows-1; i>=0; i--){
                    cltable.deleteRow(i);
                }
            }
            */
            //document.getElementById('demo').innerHTML = closed.length;
            if( sum != "0" ){
                sumheader = document.getElementById('ressum');
                if( mode == 'all'){
                    sumheader.innerHTML = '(' + sum + ') Requests';
                }
                else if( mode == 'user'){
                    sumheader.innerHTML = 'You Have (' + sum + ') Requests';
                }
                else if( mode == 'search' ){
                    sumheader.innerHTML = '(' + sum + ') Results';
                }
                else{
                    return 1;
                }

                if( open != "" ){
                    //document.getElementById('spo').textContent = open.length;
                    document.getElementById('spoo').textContent = open.length;
                    //populate(optable, open);
                    populate2(opdiv, open, sector, 2);
                }
                else{
                    //document.getElementById('spo').textContent = "0";
                    document.getElementById('spoo').textContent = "0";
                }
                if( closed != "" ){
                    //document.getElementById('spc').textContent = closed.length;
                    document.getElementById('spcc').textContent = closed.length;
                    //populate(cltable, closed);
                    populate2(cldiv, closed, sector, 2);
                }
                else{
                    //document.getElementById('spc').textContent = "0";
                    document.getElementById('spcc').textContent = "0";
                }
            }
            else{
                sumheader = document.getElementById('ressum').innerHTML = "No Requests Were Found - Please Try Again";
                //document.getElementById('spo').textContent = "0";
                //document.getElementById('spc').textContent = "0";
                document.getElementById('spoo').textContent = "0";
                document.getElementById('spcc').textContent = "0";
                //document.getElementById('allheader').innerHTML = 'No Requests Are Created Yet!';
            }
            console.log("PAGINATE " + call_for_paginate);
            if( call_for_paginate == true ){
                paginate("open");
            }
        },
        error: function () {
            document.getElementById('demo').innerHTML = 'Something isnt right!';
        }
    });
}

function populate2(div, data, sector, perpage){
    sector = parseInt(sector);
    var ranged = (sector-1)*perpage;
    var rangeu = sector*perpage;
    for( var index in data ){                   // pagination error here when all_requests -> user
        if( index >= ranged && index < rangeu ){
            var entry = data[index];
            var datadiv, a, p , img, attr, text, span;
            var entrydiv = document.createElement('div');
            entrydiv.setAttribute("class", "entry");
            div.appendChild(entrydiv);
            // first data
            datadiv = document.createElement('div');
            datadiv.setAttribute("class", "secondary");
            a = document.createElement('a');
            a.setAttribute("href", entry.id + "/");
            img = document.createElement('img');
            img.setAttribute("src", entry.file);
            img.setAttribute("id", "file");
            img.setAttribute("alt", "No File Has Been Uploaded");
            /*
            img.setAttribute("width","100px");
            img.setAttribute("height","100px");
            img.setAttribute("alt","No Image Has Been Uploaded");
            img.setAttribute("style","color: brown; float: left; margin-right: 40px;");
            */
            a.appendChild(img);
            datadiv.appendChild(a);
            entrydiv.appendChild(datadiv);
            // second td
            datadiv = document.createElement('div');
            datadiv.setAttribute("class","primary");
            a = document.createElement('a');
            a.setAttribute("href", entry.id + "/");
            attr = document.createElement("h4");
            text = document.createTextNode(entry.title);
            attr.appendChild(text);
            attr.setAttribute("class", "text-left");
            a.appendChild(attr);
            datadiv.appendChild(a);
            attr = document.createElement("hr");
            datadiv.appendChild(attr);
            p = document.createElement('p');
            span = document.createElement('span');
            span.setAttribute("class", "btn-info");
            text = document.createTextNode(entry.keywords);
            span.appendChild(text);
            text = document.createTextNode("keywords: ");
            p.appendChild(text);
            p.appendChild(span);
            p.setAttribute("class", "text-left");
            datadiv.appendChild(p);
            entrydiv.appendChild(datadiv);
            // third td
            datadiv = document.createElement('div');
            datadiv.setAttribute("class","secondary");
            p = document.createElement('p');
            text = document.createTextNode("Posted By: " + entry.user);
            p.appendChild(text);
            datadiv.appendChild(p);
            p = document.createElement('p');
            text = document.createTextNode("On: " + entry.deadline);
            p.appendChild(text);
            datadiv.appendChild(p);
            entrydiv.appendChild(datadiv);
            // fourth td
            datadiv = document.createElement('div');
            datadiv.setAttribute("class","secondary");
            p = document.createElement('p');
            text = document.createTextNode(entry.views + " views");
            p.appendChild(text);
            datadiv.appendChild(p);
            p = document.createElement('p');
            text = document.createTextNode(entry.downloads + " downloads");
            p.appendChild(text);
            datadiv.appendChild(p);
            entrydiv.appendChild(datadiv);
        }
    }
}

function populate(table, data){
    for( var index in data ){
        var entry = data[index];
        var td, a, p, text, span, attr;
        var tr = document.createElement('tr');
        table.appendChild(tr);
        // first td
        td = document.createElement('td');
        td.setAttribute("class","secondary");
        a = document.createElement('a');
        a.setAttribute("href", entry.id + "/");
        var image = document.createElement('img');
        image.setAttribute("src", entry.file);
        image.setAttribute("width","100px");
        image.setAttribute("height","100px");
        image.setAttribute("alt","No Image Has Been Uploaded");
        image.setAttribute("style","color: brown; float: left; margin-right: 40px;");
        a.appendChild(image);
        td.appendChild(a);
        tr.appendChild(td);
        // second td
        td = document.createElement('td');
        td.setAttribute("class","primary");
        a = document.createElement('a');
        a.setAttribute("href", entry.id + "/");
        attr = document.createElement("h4");
        text = document.createTextNode(entry.title);
        attr.appendChild(text);
        attr.setAttribute("class", "text-left");
        a.appendChild(attr);
        td.appendChild(a);
        attr = document.createElement("hr");
        td.appendChild(attr);
        p = document.createElement('p');
        span = document.createElement('span');
        span.setAttribute("class", "btn-info");
        text = document.createTextNode(entry.keywords);
        span.appendChild(text);
        text = document.createTextNode("keywords: ");
        p.appendChild(text);
        p.appendChild(span);
        p.setAttribute("class", "text-left");
        td.appendChild(p);
        tr.appendChild(td);
        // third td
        td = document.createElement('td');
        td.setAttribute("class","secondary");
        p = document.createElement('p');
        text = document.createTextNode("Posted By: " + entry.user);
        p.appendChild(text);
        td.appendChild(p);
        p = document.createElement('p');
        text = document.createTextNode("On: " + entry.deadline);
        p.appendChild(text);
        td.appendChild(p);
        tr.appendChild(td);
        // fourth td
        td = document.createElement('td');
        td.setAttribute("class","secondary");
        p = document.createElement('p');
        text = document.createTextNode(entry.views + " views");
        p.appendChild(text);
        td.appendChild(p);
        p = document.createElement('p');
        text = document.createTextNode(entry.downloads + " downloads");
        p.appendChild(text);
        td.appendChild(p);
        tr.appendChild(td);
    }
}

function paginate(mode){
    var sum, section;
    if( mode == "open" ){
        sum = document.getElementById("spoo").innerHTML;
        section = sectionopen;
    }
    else{
        sum = document.getElementById("spcc").innerHTML;
        section = sectionclosed;
    }
    sum = parseInt(sum);
    var paging = document.getElementById("upaging");
    var range = sum/2;
    var li, a, text;

    paging.innerHTML = "";
    paging.setAttribute("class", "pagination");

    li = document.createElement("li");
    li.setAttribute("id","previous");
    a = document.createElement("a");
    a.innerHTML = "&laquo;";
    a.setAttribute("href", "#");
    li.appendChild(a);
    paging.appendChild(li);

    console.log(" Sum " + sum );
    var i = section*5;
    var hasmore = false;

    if( i+5 < range ) {
        hasmore = true;
    }
    if( mode == "open" ){
        hasmoreopen = hasmore;
    }
    else{
        hasmoreclosed = hasmore;
    }

    for(i; i<range; i++){
        if( i == (section+1)*5 ){
            break;
        }
        li = document.createElement("li");
        if((i % 5) == 0){                                               // first page of list
            li.setAttribute("class","active");
        }
        a = document.createElement("a");
        a.innerHTML = i+1;
        a.setAttribute("href", "#");
        li.appendChild(a);
        paging.appendChild(li);
    }

    li = document.createElement("li");
    li.setAttribute("id","next");
    a = document.createElement("a");
    a.innerHTML = "&raquo;";
    a.setAttribute("href", "#");
    li.appendChild(a);
    paging.appendChild(li);
}