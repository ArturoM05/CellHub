import {
  Modal,
  Button,
  BlockStack,
  InlineStack,
  Text,
  Divider,
  EmptyState,
} from '@shopify/polaris';
import { DeleteIcon } from '@shopify/polaris-icons';
import { getBrandEmoji, formatPrice } from '../utils';

export default function CartModal({
  open,
  onClose,
  items,
  onRemove,
  onCheckout,
}) {
  const total = items.reduce((s, i) => s + i.subtotal, 0);
  const count = items.reduce((s, i) => s + i.quantity, 0);

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={`Mi carrito (${count})`}
      primaryAction={{
        content: 'Comprar ahora',
        onAction: onCheckout,
        disabled: items.length === 0,
      }}
      secondaryActions={[{ content: 'Cerrar', onAction: onClose }]}
    >
      <Modal.Section>
        {items.length === 0 ? (
          <EmptyState heading="Tu carrito está vacío">
            <p>Agrega productos desde el catálogo.</p>
          </EmptyState>
        ) : (
          <BlockStack gap="300">
            {items.map((item) => (
              <BlockStack key={item.id} gap="200">
                <InlineStack align="space-between" blockAlign="center">
                  <InlineStack gap="300" blockAlign="center">
                    <Text variant="headingLg" as="span">
                      {getBrandEmoji(item.name.split(' ')[0])}
                    </Text>
                    <BlockStack gap="050">
                      <Text variant="bodyMd" fontWeight="semibold" as="p">
                        {item.name}
                      </Text>
                      <Text variant="bodySm" tone="subdued" as="p">
                        {item.quantity}x {formatPrice(item.price)} ={' '}
                        <Text as="span" fontWeight="bold">
                          {formatPrice(item.subtotal)}
                        </Text>
                      </Text>
                    </BlockStack>
                  </InlineStack>
                  <Button
                    icon={DeleteIcon}
                    variant="plain"
                    tone="critical"
                    onClick={() => onRemove(item.id)}
                    accessibilityLabel="Eliminar"
                  />
                </InlineStack>
                <Divider />
              </BlockStack>
            ))}

            <InlineStack align="space-between">
              <Text variant="headingMd" as="span">
                Total
              </Text>
              <Text variant="headingLg" as="span">
                {formatPrice(total)}
              </Text>
            </InlineStack>
          </BlockStack>
        )}
      </Modal.Section>
    </Modal>
  );
}
