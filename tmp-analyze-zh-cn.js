const fs = require('fs');

function parsePo(content) {
  const entries = new Map();
  const blocks = content.split(/\n\n+/);
  for (const block of blocks) {
    if (!block.includes('msgid')) continue;
    const msgidMatch = block.match(/msgid "((?:[^"\\]|\\.)*)"/s);
    const msgstrMatch = block.match(/msgstr "((?:[^"\\]|\\.)*)"/s);
    if (!msgidMatch) continue;
    const msgid = msgidMatch[1].replace(/\\n/g, '\n').replace(/\\"/g, '"');
    const msgstr = msgstrMatch
      ? msgstrMatch[1].replace(/\\n/g, '\n').replace(/\\"/g, '"')
      : '';
    if (msgid === '') continue;
    entries.set(msgid, msgstr);
  }
  return entries;
}

const pairs = [
  [
    'packages/twenty-front/src/locales/zh-TW.po',
    'packages/twenty-front/src/locales/zh-CN.po',
  ],
  [
    'packages/twenty-server/src/engine/core-modules/i18n/locales/zh-TW.po',
    'packages/twenty-server/src/engine/core-modules/i18n/locales/zh-CN.po',
  ],
  [
    'packages/twenty-emails/src/locales/zh-TW.po',
    'packages/twenty-emails/src/locales/zh-CN.po',
  ],
];

for (const [twFile, cnFile] of pairs) {
  const tw = parsePo(fs.readFileSync(twFile, 'utf8'));
  const cn = parsePo(fs.readFileSync(cnFile, 'utf8'));
  let emptyTw = 0;
  let fillableFromCn = 0;
  let cnAlsoEmpty = 0;
  for (const [msgid, msgstr] of tw) {
    if (msgstr === '' || msgstr === msgid) {
      emptyTw++;
      const cnStr = cn.get(msgid);
      if (cnStr && cnStr !== '' && cnStr !== msgid) {
        fillableFromCn++;
      } else {
        cnAlsoEmpty++;
      }
    }
  }
  console.log('===', twFile, '===');
  console.log('Empty/same TW:', emptyTw);
  console.log('Fillable from zh-CN:', fillableFromCn);
  console.log('Still need translation:', cnAlsoEmpty);
}
