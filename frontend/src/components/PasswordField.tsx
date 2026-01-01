// @ts-nocheck
import { useState, forwardRef } from "react";
import { useTranslation } from "react-i18next";
import { TextField, IconButton, InputAdornment } from "@mui/material";
import { Visibility, VisibilityOff } from "@mui/icons-material";

const PasswordField = forwardRef((props, ref) => {
  const { t } = useTranslation();
  const {
    label,
    placeholder,
    error = false,
    helperText,
    autoComplete = "current-password",
    name,
    onChange,
    onBlur,
    value,
    fullWidth = true,
    variant = "outlined",
    ...rest
  } = props;

  const [showPassword, setShowPassword] = useState(false);

  const handleTogglePassword = () => {
    setShowPassword((prev) => !prev);
  };

  return (
    <TextField
      ref={ref}
      label={label || t('auth.password')}
      placeholder={placeholder}
      variant={variant}
      type={showPassword ? "text" : "password"}
      fullWidth={fullWidth}
      error={error}
      helperText={helperText}
      autoComplete={autoComplete}
      name={name}
      onChange={onChange}
      onBlur={onBlur}
      value={value}
      InputProps={{
        endAdornment: (
          <InputAdornment position="end">
            <IconButton
              aria-label={showPassword ? t('auth.hidePassword', 'Hide password') : t('auth.showPassword', 'Show password')}
              onClick={handleTogglePassword}
              edge="end"
              size="large"
              sx={{ mr: 0.5 }}
            >
              {showPassword ? <VisibilityOff /> : <Visibility />}
            </IconButton>
          </InputAdornment>
        ),
      }}
      sx={{
        '& .MuiOutlinedInput-root': {
          paddingRight: '8px',
        },
        '& .MuiInputAdornment-root': {
          marginRight: '4px',
        },
      }}
      {...rest}
    />
  );
});

PasswordField.displayName = "PasswordField";

export default PasswordField;
