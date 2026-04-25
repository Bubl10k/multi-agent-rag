import {
  Controller,
  type Control,
  type FieldValues,
  type Path,
} from 'react-hook-form';
import { TextField, type TextFieldProps } from '@mui/material';

type FormTextFieldProps<T extends FieldValues> = Omit<
  TextFieldProps,
  'name'
> & {
  name: Path<T>;
  control: Control<T>;
};

const FormTextField = <T extends FieldValues>({
  name,
  control,
  ...props
}: FormTextFieldProps<T>) => (
  <Controller
    name={name}
    control={control}
    render={({ field, fieldState }) => (
      <TextField
        {...field}
        {...props}
        fullWidth
        error={!!fieldState.error}
        helperText={fieldState.error?.message}
      />
    )}
  />
);

export default FormTextField;
