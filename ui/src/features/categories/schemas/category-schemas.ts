import { z } from "zod";

export const categorySchema = z.object({
  name: z.string().min(1, "Name is required").max(100),
});

export type CategoryFormValues = z.infer<typeof categorySchema>;
