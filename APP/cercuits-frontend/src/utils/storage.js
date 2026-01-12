// LocalStorage helper functions

// Get item from localStorage
export const getItem = (key, defaultValue = null) => {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : defaultValue;
  } catch (error) {
    console.error(`Error getting item ${key} from localStorage:`, error);
    return defaultValue;
  }
};

// Set item in localStorage
export const setItem = (key, value) => {
  try {
    localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch (error) {
    console.error(`Error setting item ${key} in localStorage:`, error);
    return false;
  }
};

// Remove item from localStorage
export const removeItem = (key) => {
  try {
    localStorage.removeItem(key);
    return true;
  } catch (error) {
    console.error(`Error removing item ${key} from localStorage:`, error);
    return false;
  }
};

// Clear all items from localStorage
export const clear = () => {
  try {
    localStorage.clear();
    return true;
  } catch (error) {
    console.error('Error clearing localStorage:', error);
    return false;
  }
};

// Check if key exists in localStorage
export const hasItem = (key) => {
  return localStorage.getItem(key) !== null;
};

// Get all keys from localStorage
export const getAllKeys = () => {
  return Object.keys(localStorage);
};

// Get storage size (approximate)
export const getStorageSize = () => {
  let total = 0;
  for (let key in localStorage) {
    if (localStorage.hasOwnProperty(key)) {
      total += localStorage[key].length + key.length;
    }
  }
  return total;
};

// Session Storage helpers
export const session = {
  getItem: (key, defaultValue = null) => {
    try {
      const item = sessionStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.error(`Error getting item ${key} from sessionStorage:`, error);
      return defaultValue;
    }
  },
  
  setItem: (key, value) => {
    try {
      sessionStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      console.error(`Error setting item ${key} in sessionStorage:`, error);
      return false;
    }
  },
  
  removeItem: (key) => {
    try {
      sessionStorage.removeItem(key);
      return true;
    } catch (error) {
      console.error(`Error removing item ${key} from sessionStorage:`, error);
      return false;
    }
  },
  
  clear: () => {
    try {
      sessionStorage.clear();
      return true;
    } catch (error) {
      console.error('Error clearing sessionStorage:', error);
      return false;
    }
  }
};
