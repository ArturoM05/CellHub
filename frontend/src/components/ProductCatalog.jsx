import { useState } from 'react';
import {
  TextField,
  Button,
  InlineStack,
  BlockStack,
  InlineGrid,
  Spinner,
  Banner,
  Text,
  Box,
} from '@shopify/polaris';
import { SearchIcon, ChevronLeftIcon, ChevronRightIcon } from '@shopify/polaris-icons';
import ProductCard from './ProductCard';
import { FILTER_OPTIONS } from '../utils';

const PROMO_SLIDES = [
  {
    title: 'Ofertas exclusivas de smartphones',
    subtitle: 'Los mejores modelos con envío rápido y garantía real.',
    image:
      'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=1200&q=80',
  },
  {
    title: 'Accesorios premium para tu celular',
    subtitle: 'Audífonos, cargadores y fundas con descuento especial.',
    image:
      'https://images.unsplash.com/photo-1512499617640-c2f99912a20f?auto=format&fit=crop&w=1200&q=80',
  },
  {
    title: 'Compra fácil, paga seguro',
    subtitle: 'Opciones de pago flexibles con el mejor respaldo.',
    image:
      'https://images.unsplash.com/photo-1491921125220-2d3d3a802bcb?auto=format&fit=crop&w=1200&q=80',
  },
];

export default function ProductCatalog({
  products,
  loading,
  error,
  search,
  onSearchChange,
  filter,
  onFilterChange,
  onAddToCart,
  addingId,
}) {
  const [slideIndex, setSlideIndex] = useState(0);

  const handleNextSlide = () => {
    setSlideIndex((prevIndex) => (prevIndex + 1) % PROMO_SLIDES.length);
  };

  const currentSlide = PROMO_SLIDES[slideIndex];

  return (
    <BlockStack gap="500">
      <div
        style={{
          width: '100%',
          minHeight: '320px',
          borderRadius: '20px',
          overflow: 'hidden',
          background: '#f4f6f8',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          textAlign: 'center',
          padding: '24px',
          boxShadow: '0 12px 24px rgba(0, 0, 0, 0.08)',
        }}
      >
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: '16px' }}>
          <Text variant="headingLg" as="h2" fontWeight="semibold">
            {currentSlide.title}
          </Text>
          <Text variant="bodyMd" tone="subdued" as="p" style={{ marginTop: '4px', maxWidth: '600px', marginLeft: 'auto', marginRight: 'auto' }}>
            {currentSlide.subtitle}
          </Text>
        </div>

        <InlineStack gap="200" align="center" blockAlign="center" style={{ marginTop: '24px' }}>
          <Button icon={ChevronLeftIcon} onClick={() => setSlideIndex((prev) => (prev - 1 + PROMO_SLIDES.length) % PROMO_SLIDES.length)} plain />
          <Button icon={ChevronRightIcon} onClick={handleNextSlide} plain />
        </InlineStack>
      </div>

      <BlockStack gap="200">
        <Text variant="heading2xl" as="h1">
          Tu próximo smartphone
        </Text>
        <Text variant="bodyLg" tone="subdued" as="p">
          Catálogo con specs reales, precios transparentes y compra en segundos.
        </Text>
      </BlockStack>

      <InlineStack gap="300" wrap blockAlign="center">
        <Box minWidth="280px">
          <TextField
            label="Buscar"
            labelHidden
            value={search}
            onChange={onSearchChange}
            placeholder="Buscar marca o modelo..."
            prefix={<SearchIcon />}
            autoComplete="off"
          />
        </Box>
        <InlineStack gap="200" wrap>
          {FILTER_OPTIONS.map((opt) => (
            <Button
              key={opt.id}
              pressed={filter === opt.id}
              onClick={() => onFilterChange(opt.id)}
            >
              {opt.label}
            </Button>
          ))}
        </InlineStack>
      </InlineStack>

      {error && (
        <Banner tone="critical" title="Error de conexión">
          <p>No se pudo conectar con la API. Corre python seed_data.py primero.</p>
        </Banner>
      )}

      {loading ? (
        <InlineStack align="center">
          <Spinner accessibilityLabel="Cargando productos" size="large" />
        </InlineStack>
      ) : products.length === 0 ? (
        <Banner tone="info">Sin resultados para tu búsqueda.</Banner>
      ) : (
        <InlineGrid columns={{ xs: 1, sm: 2, md: 3, lg: 3 }} gap="400">
          {products.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              onAdd={onAddToCart}
              adding={addingId}
            />
          ))}
        </InlineGrid>
      )}
    </BlockStack>
  );
}
