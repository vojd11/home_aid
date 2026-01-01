// @ts-nocheck
import { forwardRef } from "react";
import { useTranslation } from "react-i18next";
import { TextField } from "@mui/material";

const EmailField = forwardRef((props, ref) => {
  const { t } = useTranslation();
  const {
    label,
    placeholder,
    error = false,
    helperText,
    autoComplete = "email",
    name = "email",
    onChange,
    onBlur,
    value,
    fullWidth = true,
    variant = "outlined",
    ...rest
  } = props;

  return (
    <TextField
      ref={ref}
      label={label || t('auth.email')}
      placeholder={placeholder || t('auth.email')}
      variant={variant}
      type="email"
      fullWidth={fullWidth}
      error={error}
      helperText={helperText}
      autoComplete={autoComplete}
      name={name}
      onChange={onChange}
      onBlur={onBlur}
      value={value}
      sx={{
        '& .MuiOutlinedInput-root': {
          paddingLeft: '14px',
          paddingRight: '14px',
        },
      }}
      {...rest}
    />
  );
});

EmailField.displayName = "EmailField";

export default EmailField;
