const puppeteer = require('puppeteer')

const LIST_UA_SELECTOR = 'body > div.content-base > section > div > table > tbody > tr:nth-child(INDEX) > td.useragent > a';
const LIST_TABLE_CLASS = 'useragent';

const FILENAME = 'uas'

async function run() {
    // await calls an asynch function
    const browser = await puppeteer.launch({
        headless: false
    });
    
    const fs = require('fs');

    const page = await browser.newPage();

    await page.goto('https://developers.whatismybrowser.com/useragents/explore/software_name/chrome/');

    let listLength = await page.evaluate((sel) => {
        return document.getElementsByClassName(sel).length;
    }, LIST_TABLE_CLASS);
    
    for (let i = 1; i< listLength; i++) {
        let useragentSelector = LIST_UA_SELECTOR.replace("INDEX", i);

        let useragent = await page.evaluate((sel) => {
            let element = document.querySelector(sel)
            return element? element.innerHTML: null;
        }, useragentSelector);
        
        if (!useragent)
            continue;
        
        fs.appendFile(FILENAME, useragent+'\n', (err) => {
            if (err) throw err;
        });

        console.log(useragent);
    }
    browser.close();
}

run();

