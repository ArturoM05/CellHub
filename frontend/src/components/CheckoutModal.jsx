import { useState, useCallback, useEffect } from 'react';
import {
  Modal,
  TextField,
  Select,
  BlockStack,
  InlineStack,
  Text,
  Divider,
  Banner,
} from '@shopify/polaris';
import { apiFetch, formatPrice, PAYMENT_OPTIONS } from '../utils';

const emptyForm = {
  full_name: '',
  city: '',
  phone: '',
  street: '',
  payment_method: 'credit_card',
};

export default function CheckoutModal({
  open,
  onClose,
  items,
  token,
  user,
  showToast,
  onOrderSuccess,
}) {
  const [form, setForm] = useState({ ...emptyForm, full_name: user?.username || '' });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(null);

  const total = items.reduce((s, i) => s + i.subtotal, 0);

  useEffect(() => {
    if (open && !success) {
      setForm({ ...emptyForm, full_name: user?.username || '' });
    }
  }, [open, user, success]);

  const handleChange = useCallback((field) => (value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  }, []);

  const handleClose = () => {
    setSuccess(null);
    setForm({ ...emptyForm, full_name: user?.username || '' });
    onClose();
  };

  const handlePlaceOrder = async () => {
    const { full_name, city, phone, street, payment_method } = form;
    if (!full_name.trim() || !city.trim() || !phone.trim() || !street.trim()) {
      showToast('Completa todos los campos', true);
      return;
    }

    setLoading(true);
    const { ok, data } = await apiFetch(
      '/orders/quick-checkout/',
      {
        method: 'POST',
        body: JSON.stringify({ full_name, city, phone, street, payment_method }),
      },
      token,
    );
    setLoading(false);

    if (!ok) {
      showToast(data.error || 'Error al procesar la orden', true);
      return;
    }

    setSuccess(data);
    onOrderSuccess();
    showToast('¡Orden creada exitosamente! 🎉');
    setTimeout(handleClose, 2500);
  };

  if (success) {
    return (
      <Modal open={open} onClose={handleClose} title="Compra confirmada">
        <Modal.Section>
          <BlockStack gap="400" inlineAlign="center">
            <Text variant="heading2xl" as="p">
              🎉
            </Text>
            <Text variant="headingLg" as="h2">
              ¡Orden creada!
            </Text>
            <Text tone="subdued" as="p">
              Tu pedido fue registrado exitosamente
            </Text>
            <Banner tone="success">Orden #{success.order_id}</Banner>
            <Text as="p">
              Total:{' '}
              <Text as="span" fontWeight="bold">
                {formatPrice(success.total)}
              </Text>
            </Text>
            <Text tone="subdued" as="p">
              Puedes ver el detalle en el{' '}
              <a href="/admin/orders/order/">panel de administración</a>
            </Text>
          </BlockStack>
        </Modal.Section>
      </Modal>
    );
  }

  return (
    <Modal
      open={open}
      onClose={handleClose}
      title="Datos de envío"
      primaryAction={{
        content: 'Confirmar compra',
        onAction: handlePlaceOrder,
        loading,
      }}
      secondaryActions={[{ content: 'Cancelar', onAction: handleClose }]}
    >
      <Modal.Section>
        <BlockStack gap="400">
          <BlockStack gap="200">
            <Text variant="headingSm" as="h3">
              Resumen de orden
            </Text>
            {items.map((item) => (
              <InlineStack key={item.id} align="space-between">
                <Text as="span">
                  {item.name} x{item.quantity}
                </Text>
                <Text as="span">{formatPrice(item.subtotal)}</Text>
              </InlineStack>
            ))}
            <Divider />
            <InlineStack align="space-between">
              <Text variant="headingSm" as="span">
                Total
              </Text>
              <Text variant="headingMd" as="span">
                {formatPrice(total)}
              </Text>
            </InlineStack>
          </BlockStack>

          <TextField
            label="Nombre completo"
            value={form.full_name}
            onChange={handleChange('full_name')}
            autoComplete="name"
          />
          <InlineStack gap="300">
            <TextField
              label="Ciudad"
              value={form.city}
              onChange={handleChange('city')}
              autoComplete="address-level2"
            />
            <TextField
              label="Teléfono"
              value={form.phone}
              onChange={handleChange('phone')}
              autoComplete="tel"
            />
          </InlineStack>
          <TextField
            label="Dirección"
            value={form.street}
            onChange={handleChange('street')}
            autoComplete="street-address"
          />
          <Select
            label="Método de pago (demo)"
            options={PAYMENT_OPTIONS}
            value={form.payment_method}
            onChange={handleChange('payment_method')}
          />
        </BlockStack>
      </Modal.Section>
    </Modal>
  );
}
