const IP_SELECTOR = '#proxylisttable > tbody > tr:nth-child(INDEX) > td:nth-child(INDICE)';
const URL = 'https://free-proxy-list.net';
const NUM_PAGES = 'li.fg-button:nth-child(9) > a:nth-child(1)';
const NEXT_PAGE = '#proxylisttable_next > a:nth-child(1)';
const puppeteer = require('puppeteer');


function save_to_array(list_infos) {
    const createCsvWrite = require('csv-writer').createObjectCsvWriter;
    const csvWrite = createCsvWrite({
        path: './proxies.csv',
        header: [
            {id: 'ip', title:'IP'},
            {id: 'port', title: 'PORT'},
            {id: 'code', title:'CODE'},
            {id: 'country', title:'COUNTRY'},
            {id:'https', title:'HTTPS'}
        ]
    });
    var array_dict = [];
    for(let i=0; i<list_infos.length; i++) {
        var dict_values = {};
        var split_infos = list_infos[i].split('|');
        
        dict_values.ip = split_infos[0];
        dict_values.port = split_infos[1];
        dict_values.code = split_infos[2];
        dict_values.country = split_infos[3];
        dict_values.https = split_infos[4];
        
        array_dict.push(dict_values);
    }
    try {
        csvWrite.writeRecords(array_dict).then(
            () => {
                console.log('...File created !');
            }
        );
    } catch(error) {
        console.error(error);
    }

}

async function run() {
    const browser = await puppeteer.launch({
        headless:false
    });
    const page = await browser.newPage();

    await page.goto(URL);

    var arrayInfos = [];

    let num_pages = await page.evaluate((sel) => {
        let element = document.querySelector(sel);
        return element? element.innerHTML: null;
    }, NUM_PAGES);
    for(let pages=0; pages < parseInt(num_pages); pages++) {
        if(pages!=0) {
            await page.click(NEXT_PAGE);
        }
        for (let i=1; i <= 20; i++) {
            var infos = '';
            for(let j=0;j<6;j++) {
                if(j == 5) j+=2;
                var mapObj = {
                    INDEX:i,
                    INDICE:j
                };
                
                let selector = IP_SELECTOR.replace(/INDEX|INDICE/gi, function(matched) {
                    return mapObj[matched];
                });
                
                let result = await page.evaluate((sel) => {
                    let element = document.querySelector(sel);
                    return element? element.innerHTML: null;
                }, selector);
    
                if(!result)
                    continue;
                
                if(j==1){
                    infos+= result;
                }  else {
                    infos += '|'+result;
                }
                
            }
            arrayInfos.push(infos);
        }
    }
    
    browser.close();

    save_to_array(arrayInfos);

}

run();