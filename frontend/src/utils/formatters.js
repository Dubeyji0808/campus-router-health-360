export function getScoreColor(score) {
  const value = Number(score ?? 0);

  if (value >= 70) return 'green';
  if (value >= 40) return 'amber';
  return 'red';
}

export function getScoreLabel(score) {
  const value = Number(score ?? 0);

  if (value >= 70) return 'Healthy';
  if (value >= 40) return 'Degraded';
  return 'Critical';
}

export function formatFixType(fixString = '') {
  const normalized = String(fixString).trim();

  const map = {
    firmware_update: 'Firmware update',
    relocate: 'Relocate router',
    replace: 'Replace router',
    user_education: 'User education',
  };

  return map[normalized] || normalized.replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase());
}

export function truncateComplaint(text, maxLen = 80) {
  if (!text) return '';
  const value = String(text).trim();
  if (value.length <= maxLen) return value;
  return `${value.slice(0, maxLen).trim()}...`;
}
