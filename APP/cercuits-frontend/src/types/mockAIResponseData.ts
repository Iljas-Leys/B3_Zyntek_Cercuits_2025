// Mock data for AI Response page development
import { AIResponsePageData, AIModel, KnowledgeDocument } from '../types/aiResponse';
import { EmailPriority, EmailCategory, EmailStatus } from '../types/email';
import { MessageSender } from '../types/chat';

export const mockAIModels: AIModel[] = [
  {
    id: 'gpt4',
    name: 'gpt-4-turbo',
    displayName: 'GPT-4 Turbo',
    description: 'Most capable model',
    isActive: true,
  },
  {
    id: 'claude',
    name: 'claude-3.5-sonnet',
    displayName: 'Claude 3.5 Sonnet',
    description: 'Balanced performance',
    isActive: true,
  },
  {
    id: 'gemini',
    name: 'gemini-pro',
    displayName: 'Gemini Pro',
    description: 'Google AI model',
    isActive: true,
  },
];

export const mockKnowledgeDocuments: KnowledgeDocument[] = [
  {
    id: '1',
    title: 'ASUS ROG STRIX X570-E Manual',
    fileName: 'asus-rog-strix-x570e-manual.pdf',
    fileType: 'pdf',
    fileSize: '2.4 MB',
    category: 'BIOS Manuals',
  },
  {
    id: '2',
    title: 'BIOS 4021 Release Notes',
    fileName: 'bios-4021-notes.txt',
    fileType: 'txt',
    fileSize: '12 KB',
    category: 'Release Notes',
  },
  {
    id: '3',
    title: 'Corsair DDR4 Compatibility Matrix',
    fileName: 'corsair-compatibility.xlsx',
    fileType: 'xlsx',
    fileSize: '850 KB',
    category: 'Hardware Specs',
  },
  {
    id: '4',
    title: 'Ticket #GM-01102 (Similar Issue)',
    fileName: 'ticket-gm-01102.pdf',
    fileType: 'pdf',
    fileSize: '156 KB',
    category: 'Previous Tickets',
  },
];

export const mockAIResponseData: AIResponsePageData = {
  email: {
    id: 'email-001',
    from: 'gabriel.manifesto@techcorp.com',
    to: 'support@cercuits.com',
    subject: 'BIOS Configuration Issue - URGENT',
    body: "Hi, I'm experiencing issues with my ASUS ROG STRIX X570-E Gaming motherboard. After updating to the latest BIOS version (4021), my system won't POST. The DRAM LED stays lit, but the memory sticks were working perfectly before the BIOS update. I've tried reseating the RAM and testing each stick individually. I'm running 4 Corsair Vengeance RGB Pro 3600MHz modules. Please help - this is my work machine and I need it operational ASAP.",
    status: EmailStatus.PROCESSED,
    priority: EmailPriority.URGENT,
    category: EmailCategory.TECHNICAL,
    createdAt: new Date(Date.now() - 5 * 60 * 1000), // 5 minutes ago
    updatedAt: new Date(),
  },
  customer: {
    id: 'customer-001',
    name: 'Gabriel Manifesto',
    email: 'gabriel.manifesto@techcorp.com',
    company: 'TechCorp Solutions',
  },
  chatSession: {
    id: 'session-001',
    emailId: 'email-001',
    messages: [
      {
        id: 'msg-001',
        sessionId: 'session-001',
        content: "Hi, I'm experiencing issues with my ASUS ROG STRIX X570-E Gaming motherboard. After updating to the latest BIOS version (4021), my system won't POST. The DRAM LED stays lit, but the memory sticks were working perfectly before the BIOS update. I've tried reseating the RAM and testing each stick individually. I'm running 4 Corsair Vengeance RGB Pro 3600MHz modules. Please help - this is my work machine and I need it operational ASAP.",
        sender: MessageSender.USER,
        timestamp: new Date(Date.now() - 5 * 60 * 1000),
      },
    ],
    currentDraft: {
      id: 'draft-001',
      emailId: 'email-001',
      sessionId: 'session-001',
      content: `Hello Gabriel,

Thank you for reaching out. I understand how critical this is for your work machine. Based on your description, this appears to be a BIOS compatibility issue with your memory configuration after the update to version 4021.

**Immediate Solution:**

The ASUS ROG STRIX X570-E Gaming BIOS version 4021 has known compatibility issues with certain Corsair Vengeance RGB Pro kits running at XMP speeds. Here's what I recommend:

**1. BIOS Flashback Recovery:**
- Download BIOS version 4006 (the most stable version for your configuration) from the ASUS support page
- Format a USB drive to FAT32 and copy the BIOS file to it, renaming it to "X570EG.CAP"
- With the system powered off but PSU switched on, press and hold the Flashback button for 3 seconds

**2. Memory Configuration:**
- Install RAM in slots A2 and B2 only (2nd and 4th slots from the CPU)
- Boot into BIOS and load default settings
- Enable D.O.C.P./XMP manually in BIOS

**Why This Happened:**
BIOS version 4021 introduced stricter memory training parameters for AGESA 1.2.0.7, which can cause POST failures with RGB RAM modules.

**Estimated time:** 15-20 minutes

Best regards,
CERcuits Team`,
      sourceDocuments: [
        {
          id: 'doc-001',
          name: 'ASUS ROG STRIX X570-E Manual',
          excerpt: 'BIOS version 4021 compatibility notes...',
          relevanceScore: 0.95,
          pageNumber: 42,
        },
        {
          id: 'doc-002',
          name: 'Memory Compatibility Matrix',
          excerpt: 'Corsair Vengeance RGB Pro 3600MHz compatibility...',
          relevanceScore: 0.89,
        },
      ],
      confidence: 0.92,
      createdAt: new Date(Date.now() - 3 * 60 * 1000),
      version: 1,
    },
    status: 'active',
    createdAt: new Date(Date.now() - 5 * 60 * 1000),
    updatedAt: new Date(),
  },
  availableModels: mockAIModels,
};

// Helper function to generate a mock AI response
export const generateMockAIResponse = (userMessage: string): string => {
  // In real implementation, this would call the backend
  const responses = [
    "I understand your question. Based on the documents in our knowledge base, here's what I found...",
    "That's a great follow-up question. Let me provide more details on that specific point...",
    "I can help clarify that. According to our technical documentation...",
  ];
  
  return responses[Math.floor(Math.random() * responses.length)] + "\n\nThis is a simulated response. In production, this will come from the actual AI model.";
};