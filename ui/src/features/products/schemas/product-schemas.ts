import { z } from "zod";

export const productFormSchema = z.object({
  name: z.string().min(1, "Name is required").max(200),
  description: z.string().optional(),
  price: z.number({ error: "Price is required" }).min(0, "Price must be >= 0"),
  stock_quantity: z.number({ error: "Stock is required" }).int().min(0, "Stock must be >= 0"),
  category_id: z.string().uuid("Select a category"),
  is_active: z.boolean(),
});

export const stockDeltaSchema = z.object({
  delta: z.number({ error: "Delta is required" }).int().refine((value) => value !== 0, "Delta cannot be zero"),
});

export type ProductFormValues = z.infer<typeof productFormSchema>;
export type StockDeltaFormValues = z.infer<typeof stockDeltaSchema>;
