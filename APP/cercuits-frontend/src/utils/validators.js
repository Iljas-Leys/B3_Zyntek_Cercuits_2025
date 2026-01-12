// Email validation
export const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

// Required field validation
export const validateRequired = (value) => {
  if (typeof value === 'string') {
    return value.trim().length > 0;
  }
  return value != null;
};

// Min length validation
export const validateMinLength = (value, minLength) => {
  if (typeof value !== 'string') return false;
  return value.length >= minLength;
};

// Max length validation
export const validateMaxLength = (value, maxLength) => {
  if (typeof value !== 'string') return false;
  return value.length <= maxLength;
};

// URL validation
export const validateURL = (url) => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

// Phone number validation (basic)
export const validatePhone = (phone) => {
  const re = /^[\d\s\-\+\(\)]+$/;
  return re.test(phone) && phone.replace(/\D/g, '').length >= 10;
};

// Password validation
export const validatePassword = (password) => {
  // At least 8 characters, 1 uppercase, 1 lowercase, 1 number
  const re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/;
  return re.test(password);
};

// Form validation
export const validateForm = (values, rules) => {
  const errors = {};
  
  Object.keys(rules).forEach(field => {
    const rule = rules[field];
    const value = values[field];
    
    if (rule.required && !validateRequired(value)) {
      errors[field] = `${field} is required`;
    }
    
    if (rule.email && !validateEmail(value)) {
      errors[field] = 'Invalid email address';
    }
    
    if (rule.minLength && !validateMinLength(value, rule.minLength)) {
      errors[field] = `Must be at least ${rule.minLength} characters`;
    }
    
    if (rule.maxLength && !validateMaxLength(value, rule.maxLength)) {
      errors[field] = `Must be no more than ${rule.maxLength} characters`;
    }
  });
  
  return errors;
};
