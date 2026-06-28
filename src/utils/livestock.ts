const LIVESTOCK_DISPLAY_LABEL_BY_TYPE: Record<string, string> = {
  기타가금: '기타',
  기타가금류: '기타',
};

export function getLivestockDisplayLabel(livestockType: string) {
  return LIVESTOCK_DISPLAY_LABEL_BY_TYPE[livestockType] ?? livestockType;
}
