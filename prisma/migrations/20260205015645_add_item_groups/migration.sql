-- CreateTable
CREATE TABLE "item_groups" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "item_groups_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "item_group_items" (
    "id" TEXT NOT NULL,
    "groupId" TEXT NOT NULL,
    "inventoryItemId" TEXT NOT NULL,
    "quantity" INTEGER NOT NULL DEFAULT 1,
    "notes" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "item_group_items_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "item_group_items_groupId_idx" ON "item_group_items"("groupId");

-- CreateIndex
CREATE INDEX "item_group_items_inventoryItemId_idx" ON "item_group_items"("inventoryItemId");

-- CreateIndex
CREATE UNIQUE INDEX "item_group_items_groupId_inventoryItemId_key" ON "item_group_items"("groupId", "inventoryItemId");

-- AddForeignKey
ALTER TABLE "item_group_items" ADD CONSTRAINT "item_group_items_groupId_fkey" FOREIGN KEY ("groupId") REFERENCES "item_groups"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "item_group_items" ADD CONSTRAINT "item_group_items_inventoryItemId_fkey" FOREIGN KEY ("inventoryItemId") REFERENCES "inventory_items"("id") ON DELETE CASCADE ON UPDATE CASCADE;
