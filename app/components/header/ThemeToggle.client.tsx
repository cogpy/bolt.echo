import { useStore } from '@nanostores/react';
import { themeStore, toggleTheme } from '~/lib/stores/theme';
import { classNames } from '~/utils/classNames';

export function ThemeToggle() {
  const theme = useStore(themeStore);
  const isDark = theme === 'dark';

  return (
    <button
      onClick={toggleTheme}
      className={classNames(
        'flex items-center justify-center p-2 rounded-md transition-colors',
        'hover:bg-bolt-elements-item-backgroundActive',
        'text-bolt-elements-textSecondary hover:text-bolt-elements-textPrimary'
      )}
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      {isDark ? (
        <div className="i-ph:sun-duotone text-xl" />
      ) : (
        <div className="i-ph:moon-duotone text-xl" />
      )}
    </button>
  );
}
