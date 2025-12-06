// Avatar utility functions and mappings for The Hive
// Used across profile pages, navbar, and offer/need cards

export const AVATAR_EMOJIS: Record<string, string> = {
  // Insects
  bee: '🐝',
  butterfly: '🦋',
  ladybug: '🐞',
  ant: '🐜',
  cricket: '🦗',
  caterpillar: '🐛',
  snail: '🐌',
  spider: '🕷️',
  mosquito: '🦟',
  // Nature/animals
  bird: '🐦',
  owl: '🦉',
  turtle: '🐢',
  frog: '🐸',
  rabbit: '🐰',
  fox: '🦊',
  bear: '🐻',
  wolf: '🐺',
  deer: '🦌',
  squirrel: '🐿️',
  // Plants
  flower: '🌸',
  sunflower: '🌻',
  tree: '🌳',
  leaf: '🍃',
  mushroom: '🍄',
  cactus: '🌵',
}

export const AVATAR_COLORS: Record<string, string> = {
  // Insects
  bee: '#FFD700',
  butterfly: '#E91E63',
  ladybug: '#F44336',
  ant: '#795548',
  cricket: '#8BC34A',
  caterpillar: '#4CAF50',
  snail: '#9E9E9E',
  spider: '#424242',
  mosquito: '607D8B',
  // Nature/animals
  bird: '#03A9F4',
  owl: '#8D6E63',
  turtle: '#009688',
  frog: '#8BC34A',
  rabbit: '#FFCCBC',
  fox: '#FF5722',
  bear: '#795548',
  wolf: '#78909C',
  deer: '#A1887F',
  squirrel: '#FF8A65',
  // Plants
  flower: '#F48FB1',
  sunflower: '#FFC107',
  tree: '#4CAF50',
  leaf: '#81C784',
  mushroom: '#D7CCC8',
  cactus: '#66BB6A',
}

export const PRESET_AVATARS = Object.keys(AVATAR_EMOJIS)

export interface AvatarDisplay {
  isCustomImage?: boolean
  src?: string
  emoji?: string
  bgcolor?: string
}

/**
 * Get avatar display information based on profile image settings
 * @param profileImage - The profile image value (preset name or data URL)
 * @param profileImageType - 'preset' or 'custom'
 * @returns Avatar display info or null if no valid avatar
 */
export function getAvatarDisplay(
  profileImage: string | null | undefined,
  profileImageType: string | null | undefined
): AvatarDisplay | null {
  // Custom image (data URL or URL)
  if (profileImageType === 'custom' && profileImage) {
    return { isCustomImage: true, src: profileImage }
  }
  // Preset emoji avatar
  if (profileImageType === 'preset' && profileImage && AVATAR_EMOJIS[profileImage]) {
    return {
      emoji: AVATAR_EMOJIS[profileImage],
      bgcolor: AVATAR_COLORS[profileImage],
    }
  }
  return null
}

/**
 * Get emoji for a preset avatar name
 */
export function getAvatarEmoji(presetName: string): string {
  return AVATAR_EMOJIS[presetName] || presetName[0].toUpperCase()
}

/**
 * Get background color for a preset avatar name
 */
export function getAvatarColor(presetName: string): string {
  return AVATAR_COLORS[presetName] || '#9E9E9E'
}
