import xlsx from 'xlsx';
import path from 'path';

export const load = async () => {
  const filePath = path.resolve('./scripts/output.xlsx');
  const workbook = xlsx.readFile(filePath);
  const sheetName = workbook.SheetNames[0];
  const rawData = xlsx.utils.sheet_to_json(workbook.Sheets[sheetName]);

  const formatDate = (val) => {
    if (val instanceof Date) {
      return `${val.getDate().toString().padStart(2, '0')}-${(val.getMonth() + 1).toString().padStart(2, '0')}-${val.getFullYear()}`;
    }
    return val;
  };

  const toDateObject = (val) => {
    if (val instanceof Date) return val;
    if (typeof val === 'string') {
      const [day, month, year] = val.split('-').map(Number);
      return new Date(year, month - 1, day);
    }
    return new Date(val);
  };

  const uniqueWeeks = [...new Set(rawData.map((d) => formatDate(d['Week van'])))];

  const sortedWeeks = uniqueWeeks.sort((a, b) => {
    return toDateObject(a) - toDateObject(b);
  });

  const names = [...new Set(rawData.map((d) => d.Naam))].sort();

  const simplifiedRaw = rawData.map((row) => ({
    'Week van': formatDate(row['Week van']),
    Naam: row.Naam,
    Dag: row.Dag
  }));

  return {
    weeks: sortedWeeks,
    names: names,
    rawData: simplifiedRaw
  };
};
