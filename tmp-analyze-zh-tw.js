const fs = require('fs');

function parsePo(content) {
  const entries = [];
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
    entries.push({ msgid, msgstr });
  }
  return entries;
}

function hasEnglish(text) {
  return /[A-Za-z]{3,}/.test(text);
}

const files = [
  'packages/twenty-front/src/locales/zh-TW.po',
  'packages/twenty-server/src/engine/core-modules/i18n/locales/zh-TW.po',
  'packages/twenty-emails/src/locales/zh-TW.po',
];

for (const file of files) {
  const content = fs.readFileSync(file, 'utf8');
  const entries = parsePo(content);
  const empty = entries.filter((entry) => entry.msgstr === '');
  const sameAsId = entries.filter(
    (entry) => entry.msgstr === entry.msgid && entry.msgid !== '',
  );
  const englishInStr = entries.filter(
    (entry) =>
      entry.msgstr !== '' &&
      hasEnglish(entry.msgstr) &&
      entry.msgstr !== entry.msgid,
  );
  console.log('===', file, '===');
  console.log('Total entries:', entries.length);
  console.log('Empty msgstr:', empty.length);
  console.log('Same as msgid:', sameAsId.length);
  console.log('English in msgstr:', englishInStr.length);
}
