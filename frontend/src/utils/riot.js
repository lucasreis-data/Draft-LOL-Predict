const RIOT_VERSION = '16.18.1';
const RIOT_ID_MAP = {
  "Bel'Veth": 'Belveth', "Cho'Gath": 'Chogath', "Kai'Sa": 'Kaisa', "Kha'Zix": 'Khazix', "Vel'Koz": 'Velkoz',
  'LeBlanc': 'Leblanc', 'Wukong': 'MonkeyKing', 'Nunu & Willump': 'Nunu', 'Renata Glasc': 'Renata',
};

export function riotId(name) {
  if (!name) return '';
  return RIOT_ID_MAP[name] || name.replace(/[^a-zA-Z0-9]/g, '');
}

export function champImg(name) {
  if (!name) return '';
  return `https://ddragon.leagueoflegends.com/cdn/${RIOT_VERSION}/img/champion/${riotId(name)}.png`;
}

export function champSplash(name) {
  if (!name) return '';
  return `https://ddragon.leagueoflegends.com/cdn/img/champion/splash/${riotId(name)}_0.jpg`;
}

export function fuzzyMatch(query, target) {
  if (!query) return true;
  if (!target) return false;
  query = query.toLowerCase();
  target = target.toLowerCase();
  let qi = 0;
  for (let ti = 0; ti < target.length && qi < query.length; ti++) {
    if (target[ti] === query[qi]) qi++;
  }
  return qi === query.length;
}

export function initials(name) {
  if (!name) return '';
  return name.split(/[\s']/).filter(Boolean).map(w => w[0]).join('').slice(0, 2).toUpperCase();
}

export function hashStr(s) {
  if (!s) return 0;
  let h = 0;
  for (let i = 0; i < s.length; i++) {
    h = (h * 31 + s.charCodeAt(i)) | 0;
  }
  return Math.abs(h);
}

export const PALETTE = [
  'linear-gradient(135deg,#3a1c5e,#1a0d2e)', 'linear-gradient(135deg,#1c4a5e,#0d222e)',
  'linear-gradient(135deg,#5e1c2e,#2e0d16)', 'linear-gradient(135deg,#1c5e3a,#0d2e1a)',
  'linear-gradient(135deg,#5e4a1c,#2e230d)', 'linear-gradient(135deg,#1c2e5e,#0d162e)',
  'linear-gradient(135deg,#4a1c5e,#230d2e)', 'linear-gradient(135deg,#5e1c1c,#2e0d0d)'
];
