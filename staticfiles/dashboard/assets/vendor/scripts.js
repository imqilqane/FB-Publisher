let addnewaccount = document.getElementById('addnewaccount'),
    addaccoutform = document.getElementById('addaccoutform'),
    loder = document.getElementById('loader'),
    loder2 = document.getElementById('loader2'),
    hide_section = document.getElementById('hide_section'),
    note = document.getElementById('note'),
    alert_btn = document.getElementById('alert'),
    gourps_list = document.getElementById('gourps_list'),
    StartJoinGroups = document.getElementById('StartJoinGroups'),
    check_groups_status = document.getElementById('check_groups_status'),
    Check_Posting_Permestion_status = document.getElementById('Check_Posting_Permestion_status'),
    start_load = document.getElementById('start_load');
    start_load2 = document.getElementById('start_load2');


console.log(start_load)
console.log(start_load)

if (addnewaccount != null){
    addnewaccount.addEventListener('click', (e) => {
        addnewaccount.style.display = 'none';
        addaccoutform.style.display = 'block';
        note.style.display = 'block';
    });
}


if (StartJoinGroups != null){
    StartJoinGroups.addEventListener('click', (e) => {
        console.log('hahahahaha')
        StartJoinGroups.style.display = 'none';
        loder.style.display = 'block';
        alert_btn.style.display = 'none';
        gourps_list.style.display = 'block';
    });
}

if (start_load != null){
    start_load.addEventListener('click', (e) => {
        if (addaccoutform != null){
            addaccoutform.style.display = 'none';
        } else {
            check_groups_status.style.display = 'none';
        }
        loder.style.display = 'block';
    });
}

if (start_load2 != null){
    start_load2.addEventListener('click', (e) => {
        Check_Posting_Permestion_status.style.display = 'none';
        loder2.style.display = 'block';
    });
}

