import {
  Modal,
  TextField,
  Button,
  BlockStack,
  InlineStack,
  Text,
  Tabs,
} from '@shopify/polaris';
import { useState, useCallback } from 'react';
import { apiFetch } from '../utils';

const emptyLogin = { username: '', password: '' };
const emptyRegister = {
  first_name: '',
  last_name: '',
  username: '',
  email: '',
  phone: '',
  password: '',
  password2: '',
};

export default function AuthModal({ open, onClose, onAuthSuccess, showToast }) {
  const [tab, setTab] = useState(0);
  const [login, setLogin] = useState(emptyLogin);
  const [register, setRegister] = useState(emptyRegister);
  const [loading, setLoading] = useState(false);

  const handleLoginChange = useCallback((field) => (value) => {
    setLogin((prev) => ({ ...prev, [field]: value }));
  }, []);

  const handleRegisterChange = useCallback((field) => (value) => {
    setRegister((prev) => ({ ...prev, [field]: value }));
  }, []);

  const handleLogin = async () => {
    setLoading(true);
    const { ok, data } = await apiFetch('/users/guest-login/', {
      method: 'POST',
      body: JSON.stringify(login),
    });
    setLoading(false);

    if (!ok) {
      showToast(data.error || 'Credenciales incorrectas', true);
      return;
    }

    onAuthSuccess(data.access, data.user);
    onClose();
    showToast('¡Bienvenido, ' + data.user.username + '! 👋');
    setLogin(emptyLogin);
  };

  const handleRegister = async () => {
    setLoading(true);
    const { ok, data } = await apiFetch('/users/register/', {
      method: 'POST',
      body: JSON.stringify({
        username: register.username,
        email: register.email,
        first_name: register.first_name,
        last_name: register.last_name,
        phone: register.phone,
        password: register.password,
        password2: register.password2,
      }),
    });

    if (!ok) {
      setLoading(false);
      const errors = Object.values(data).flat().join(' ');
      showToast(errors || 'Error al registrarse', true);
      return;
    }

    const loginRes = await apiFetch('/users/guest-login/', {
      method: 'POST',
      body: JSON.stringify({
        username: register.username,
        password: register.password,
      }),
    });
    setLoading(false);

    if (loginRes.ok) {
      onAuthSuccess(loginRes.data.access, loginRes.data.user);
      onClose();
      showToast('¡Cuenta creada! Bienvenido 🎉');
      setRegister(emptyRegister);
    }
  };

  const handleSubmit = () => {
    if (tab === 0) handleLogin();
    else handleRegister();
  };

  const tabs = [
    { id: 'login', content: 'Iniciar sesión' },
    { id: 'register', content: 'Registrarse' },
  ];

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={tab === 0 ? 'Acceder a CellHub' : 'Crear cuenta'}
      primaryAction={{
        content: tab === 0 ? 'Iniciar sesión' : 'Crear cuenta',
        onAction: handleSubmit,
        loading,
      }}
      secondaryActions={[{ content: 'Cancelar', onAction: onClose }]}
    >
      <Modal.Section>
        <BlockStack gap="400">
          <Tabs tabs={tabs} selected={tab} onSelect={setTab} />

          {tab === 0 ? (
            <BlockStack gap="300">
              <TextField
                label="Usuario"
                value={login.username}
                onChange={handleLoginChange('username')}
                autoComplete="username"
              />
              <TextField
                label="Contraseña"
                type="password"
                value={login.password}
                onChange={handleLoginChange('password')}
                autoComplete="current-password"
              />
              <Text as="p" tone="subdued">
                ¿No tienes cuenta?{' '}
                <Button variant="plain" onClick={() => setTab(1)}>
                  Regístrate gratis
                </Button>
              </Text>
            </BlockStack>
          ) : (
            <BlockStack gap="300">
              <InlineStack gap="300">
                <TextField
                  label="Nombre"
                  value={register.first_name}
                  onChange={handleRegisterChange('first_name')}
                  autoComplete="given-name"
                />
                <TextField
                  label="Apellido"
                  value={register.last_name}
                  onChange={handleRegisterChange('last_name')}
                  autoComplete="family-name"
                />
              </InlineStack>
              <TextField
                label="Usuario"
                value={register.username}
                onChange={handleRegisterChange('username')}
                autoComplete="username"
              />
              <TextField
                label="Email"
                type="email"
                value={register.email}
                onChange={handleRegisterChange('email')}
                autoComplete="email"
              />
              <TextField
                label="Teléfono"
                value={register.phone}
                onChange={handleRegisterChange('phone')}
                autoComplete="tel"
              />
              <TextField
                label="Contraseña"
                type="password"
                value={register.password}
                onChange={handleRegisterChange('password')}
                autoComplete="new-password"
              />
              <TextField
                label="Confirmar contraseña"
                type="password"
                value={register.password2}
                onChange={handleRegisterChange('password2')}
                autoComplete="new-password"
              />
              <Text as="p" tone="subdued">
                ¿Ya tienes cuenta?{' '}
                <Button variant="plain" onClick={() => setTab(0)}>
                  Inicia sesión
                </Button>
              </Text>
            </BlockStack>
          )}
        </BlockStack>
      </Modal.Section>
    </Modal>
  );
}
