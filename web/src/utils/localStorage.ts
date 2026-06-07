const setItemToStorage = (key: string, object: any) => {
  const data = JSON.stringify(object);

  if (data) {
    return localStorage.setItem(key, data);
  } else {
    return false;
  }
};

const getItemFromStorage = (key: string) => {
  const data = localStorage.getItem(key);

  if (data) {
    return JSON.parse(data);
  } else {
    return null;
  }
};

export const localStorageService = {
  setSidebarCollapsed: (value: boolean) => setItemToStorage('sidebarCollapsed', value),
  getSidebarCollapsed: () => getItemFromStorage('sidebarCollapsed'),

  setLanguage: (value: string) => setItemToStorage('language', value),
  getLanguage: (): string | null => getItemFromStorage('language'),

  setAuthToken: (token: string) => setItemToStorage('auth_token', token),
  getAuthToken: (): string | null => getItemFromStorage('auth_token'),
  removeAuthToken: () => localStorage.removeItem('auth_token'),

  setRefreshToken: (token: string) => setItemToStorage('refresh_token', token),
  getRefreshToken: (): string | null => getItemFromStorage('refresh_token'),
  removeRefreshToken: () => localStorage.removeItem('refresh_token'),

  setAuthUser: (user: object) => setItemToStorage('auth_user', user),
  getAuthUser: <T>(): T | null => getItemFromStorage('auth_user'),
  removeAuthUser: () => localStorage.removeItem('auth_user'),

  clear: () => localStorage.clear(),
};
