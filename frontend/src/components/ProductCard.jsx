import {
  Card,
  Text,
  Badge,
  Button,
  InlineStack,
  BlockStack,
  Box,
} from '@shopify/polaris';
import { formatPrice } from '../utils';

export default function ProductCard({ product, onAdd, adding }) {
  const {
    id,
    brand,
    model_name,
    os,
    ram_gb,
    storage_gb,
    camera_mp,
    battery_mah,
    price,
    image,
  } = product;

  return (
    <Card>
      <BlockStack gap="300">
        <Box
          background="bg-surface-secondary"
          padding="0"
          borderRadius="200"
          style={{
            overflow: 'hidden',
            position: 'relative',
            height: '160px',
            backgroundColor: image ? undefined : '#f4f6f8',
          }}
        >
          {image ? (
            <>
              <img
                src={image}
                alt={`${brand} ${model_name}`}
                loading="lazy"
                onError={(event) => {
                  event.currentTarget.onerror = null;
                  event.currentTarget.src =
                    'https://via.placeholder.com/640x360.png?text=Imagen+no+disponible';
                }}
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                  display: 'block',
                }}
              />
              <Box
                style={{
                  position: 'absolute',
                  top: '1rem',
                  left: '1rem',
                }}
              >
                <Badge tone={os === 'ios' ? 'info' : 'success'}>
                  {os === 'ios' ? 'iOS' : 'Android'}
                </Badge>
              </Box>
            </>
          ) : (
            <InlineStack align="space-between" blockAlign="start">
              <Text variant="bodyMd" tone="subdued">
                Sin imagen
              </Text>
              <Badge tone={os === 'ios' ? 'info' : 'success'}>
                {os === 'ios' ? 'iOS' : 'Android'}
              </Badge>
            </InlineStack>
          )}
        </Box>

        <BlockStack gap="100">
          <Text variant="bodySm" tone="subdued" as="p">
            {brand}
          </Text>
          <Text variant="headingMd" as="h3">
            {model_name}
          </Text>
        </BlockStack>

        <InlineStack gap="200" wrap>
          <Badge>{ram_gb}GB RAM</Badge>
          <Badge>{storage_gb}GB</Badge>
          <Badge>{camera_mp}MP</Badge>
          <Badge>{battery_mah}mAh</Badge>
        </InlineStack>

        <InlineStack align="space-between" blockAlign="center">
          <BlockStack gap="050">
            <Text variant="headingLg" as="p">
              {formatPrice(price)}
            </Text>
            <Text variant="bodySm" tone="subdued" as="p">
              IVA incluido
            </Text>
          </BlockStack>
          <Button
            variant="primary"
            onClick={() => onAdd(id, `${brand} ${model_name}`, price)}
            loading={adding === id}
            disabled={adding === id}
          >
            Agregar
          </Button>
        </InlineStack>
      </BlockStack>
    </Card>
  );
}
