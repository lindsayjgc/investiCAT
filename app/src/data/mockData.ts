import { Entity, Event, Investigation } from '@/types/investigation';

export const mockEntities: Entity[] = [
  {
    id: '1',
    name: 'John Mitchell',
    type: 'person',
    description: 'CEO of TechCorp',
    color: '#3B82F6'
  },
  {
    id: '2',
    name: 'Sarah Chen',
    type: 'person',
    description: 'CFO of TechCorp',
    color: '#8B5CF6'
  },
  {
    id: '3',
    name: 'TechCorp Industries',
    type: 'organization',
    description: 'Technology company',
    color: '#10B981'
  },
  {
    id: '4',
    name: 'Offshore Bank Ltd',
    type: 'organization',
    description: 'Financial institution',
    color: '#F59E0B'
  },
  {
    id: '5',
    name: 'Manhattan Office',
    type: 'location',
    description: 'Corporate headquarters',
    color: '#EF4444'
  },
  {
    id: '6',
    name: 'Swiss Account #4429',
    type: 'object',
    description: 'Bank account',
    color: '#06B6D4'
  }
];

export const mockEvents: Event[] = [
  {
    id: 'e1',
    title: 'Initial Meeting - Project Genesis',
    description: 'John Mitchell and Sarah Chen met to discuss the new project codenamed "Genesis". They discussed budget allocation and timeline requirements.',
    date: new Date('2024-01-15T09:00:00'),
    location: 'Manhattan Office, Conference Room A',
    entities: [mockEntities[0], mockEntities[1], mockEntities[4]],
    category: 'meeting',
    priority: 'medium',
    dependencies: [],
    sourceDocument: 'meeting_notes_jan15.pdf',
    confidence: 0.95
  },
  {
    id: 'e2',
    title: 'Email Exchange - Budget Concerns',
    description: 'Sarah Chen sent an email to John Mitchell expressing concerns about the project budget exceeding initial estimates by 40%.',
    date: new Date('2024-01-18T14:30:00'),
    location: undefined,
    entities: [mockEntities[0], mockEntities[1]],
    category: 'communication',
    priority: 'high',
    dependencies: ['e1'],
    sourceDocument: 'email_thread_budget.pdf',
    confidence: 0.88
  },
  {
    id: 'e3',
    title: 'Wire Transfer - Project Funding',
    description: 'Large wire transfer of $2.5M from TechCorp to Offshore Bank Ltd for project funding. Transfer reference: GENESIS-FUND-001.',
    date: new Date('2024-01-22T11:15:00'),
    location: undefined,
    entities: [mockEntities[2], mockEntities[3], mockEntities[5]],
    category: 'transaction',
    priority: 'critical',
    dependencies: ['e1', 'e2'],
    sourceDocument: 'bank_statement_jan.pdf',
    confidence: 0.99
  },
  {
    id: 'e4',
    title: 'Contract Amendment Signed',
    description: 'Amendment to the original Genesis project contract was signed, increasing the scope and budget allocation. New timeline extends to Q3 2024.',
    date: new Date('2024-01-25T16:45:00'),
    location: 'Manhattan Office, Legal Department',
    entities: [mockEntities[0], mockEntities[1], mockEntities[2], mockEntities[4]],
    category: 'document',
    priority: 'high',
    dependencies: ['e3'],
    sourceDocument: 'contract_amendment_v2.pdf',
    confidence: 0.92
  },
  {
    id: 'e5',
    title: 'Emergency Board Call',
    description: 'Unscheduled board call was held to discuss irregularities found in the Genesis project financial audit. Duration: 2 hours.',
    date: new Date('2024-02-03T08:00:00'),
    location: undefined,
    entities: [mockEntities[0], mockEntities[1], mockEntities[2]],
    category: 'meeting',
    priority: 'critical',
    dependencies: ['e3', 'e4'],
    sourceDocument: 'board_call_transcript_feb3.pdf',
    confidence: 0.91
  },
  {
    id: 'e6',
    title: 'Suspicious Account Activity',
    description: 'Multiple small withdrawals totaling $150K detected from Swiss Account #4429. Withdrawals made across different ATMs in Geneva.',
    date: new Date('2024-02-05T12:20:00'),
    location: 'Geneva, Switzerland',
    entities: [mockEntities[5]],
    category: 'transaction',
    priority: 'critical',
    dependencies: ['e3'],
    sourceDocument: 'atm_transaction_log.pdf',
    confidence: 0.87
  },
  {
    id: 'e7',
    title: 'Internal Audit Report Filed',
    description: 'Internal audit team completed their investigation into Genesis project financials. Report flagged several concerning discrepancies.',
    date: new Date('2024-02-10T17:30:00'),
    location: 'Manhattan Office, Audit Department',
    entities: [mockEntities[2], mockEntities[4]],
    category: 'document',
    priority: 'high',
    dependencies: ['e5', 'e6'],
    sourceDocument: 'internal_audit_report_genesis.pdf',
    confidence: 0.96
  },
  {
    id: 'e8',
    title: 'John Mitchell Resignation',
    description: 'John Mitchell submitted his resignation as CEO, citing personal reasons. Resignation effective immediately with severance package.',
    date: new Date('2024-02-12T09:15:00'),
    location: 'Manhattan Office, HR Department',
    entities: [mockEntities[0], mockEntities[2], mockEntities[4]],
    category: 'action',
    priority: 'critical',
    dependencies: ['e7'],
    sourceDocument: 'resignation_letter_mitchell.pdf',
    confidence: 0.99
  }
];

export const mockInvestigation: Investigation = {
  id: 'inv-1',
  title: 'TechCorp Genesis Project Investigation',
  description: 'Investigation into financial irregularities and potential fraud in the Genesis project at TechCorp Industries.',
  createdAt: new Date('2024-01-10'),
  updatedAt: new Date('2024-02-15'),
  events: mockEvents,
  entities: mockEntities,
  documents: [
    {
      id: 'doc-1',
      name: 'meeting_notes_jan15.pdf',
      type: 'application/pdf',
      size: 245760,
      uploadedAt: new Date('2024-01-16'),
      processed: true,
      extractedEvents: ['e1']
    },
    {
      id: 'doc-2',
      name: 'email_thread_budget.pdf',
      type: 'application/pdf',
      size: 128340,
      uploadedAt: new Date('2024-01-19'),
      processed: true,
      extractedEvents: ['e2']
    },
    {
      id: 'doc-3',
      name: 'bank_statement_jan.pdf',
      type: 'application/pdf',
      size: 456780,
      uploadedAt: new Date('2024-01-23'),
      processed: true,
      extractedEvents: ['e3', 'e6']
    }
  ]
};