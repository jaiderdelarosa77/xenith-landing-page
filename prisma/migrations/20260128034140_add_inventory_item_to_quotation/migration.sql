-- AlterTable
ALTER TABLE "quotation_items" ADD COLUMN     "inventoryItemId" TEXT;

-- CreateIndex
CREATE INDEX "quotation_items_inventoryItemId_idx" ON "quotation_items"("inventoryItemId");

-- AddForeignKey
ALTER TABLE "quotation_items" ADD CONSTRAINT "quotation_items_inventoryItemId_fkey" FOREIGN KEY ("inventoryItemId") REFERENCES "inventory_items"("id") ON DELETE SET NULL ON UPDATE CASCADE;
