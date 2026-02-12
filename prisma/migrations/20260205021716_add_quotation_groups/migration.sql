-- CreateTable
CREATE TABLE "quotation_groups" (
    "id" TEXT NOT NULL,
    "quotationId" TEXT NOT NULL,
    "groupId" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "unitPrice" DECIMAL(10,2) NOT NULL,
    "quantity" INTEGER NOT NULL DEFAULT 1,
    "total" DECIMAL(10,2) NOT NULL,
    "order" INTEGER NOT NULL DEFAULT 0,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "quotation_groups_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "quotation_groups_quotationId_idx" ON "quotation_groups"("quotationId");

-- CreateIndex
CREATE INDEX "quotation_groups_groupId_idx" ON "quotation_groups"("groupId");

-- AddForeignKey
ALTER TABLE "quotation_groups" ADD CONSTRAINT "quotation_groups_quotationId_fkey" FOREIGN KEY ("quotationId") REFERENCES "quotations"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "quotation_groups" ADD CONSTRAINT "quotation_groups_groupId_fkey" FOREIGN KEY ("groupId") REFERENCES "item_groups"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
