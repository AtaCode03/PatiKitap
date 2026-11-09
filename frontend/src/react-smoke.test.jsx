import React from 'react';
import {render, screen} from '@testing-library/react';
import {test, expect} from 'vitest';

test('PatiKitap React bileşeni görüntülenir', () => {
  render(<h1>PatiKitap Test</h1>);
  expect(screen.getByText('PatiKitap Test')).toBeInTheDocument();
});
