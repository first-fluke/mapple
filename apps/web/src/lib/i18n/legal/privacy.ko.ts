import type { LegalDoc } from './types';

export const privacyKo: LegalDoc = {
  title: '개인정보처리방침',
  lastUpdated: '2026-05-03',
  lastUpdatedLabel: '최종 수정일:',
  intro:
    '본 방침 초안은 Globe CRM v1 출시를 위한 임시 본문이며, 정식 서비스 개시 전 법무 검토를 거쳐 갱신될 예정입니다.',
  sections: [
    {
      heading: '1. 수집하는 개인정보',
      items: [
        'OAuth 제공자(Google, GitHub)에서 전달받는 이메일, 이름, 프로필 사진',
        '사용자가 직접 입력한 컨택트, 미팅, 조직, 경력 데이터',
        '서비스 이용 과정에서 자동 생성되는 세션 쿠키 및 접속 로그',
      ],
    },
    {
      heading: '2. 이용 목적',
      items: ['로그인 및 본인 확인', '사용자가 등록한 데이터의 저장·표시·검색 제공', '오류 분석 및 서비스 품질 개선'],
    },
    {
      heading: '3. 보관 기간',
      paragraphs: [
        '계정이 활성 상태인 동안 보관하며, 사용자가 계정 삭제를 요청하면 30일 이내에 모든 개인정보 및 사용자 콘텐츠를 영구 삭제합니다. 단, 법령에 따라 보관이 의무화된 항목은 그 기간을 따릅니다.',
      ],
    },
    {
      heading: '4. 제3자 제공',
      paragraphs: ['운영자는 사용자 동의 또는 법령에 근거한 경우 외에 사용자 정보를 제3자에게 제공하지 않습니다.'],
    },
    {
      heading: '5. 처리 위탁',
      paragraphs: [
        '서비스 운영을 위해 다음의 위탁업체를 사용합니다: Google Cloud Platform(인프라), Fly.io(API 호스팅), Vercel(웹 호스팅), Cloudflare(DNS/CDN), Sentry(에러 트래킹).',
      ],
    },
    {
      heading: '6. 사용자 권리',
      items: ['개인정보 열람, 정정, 삭제, 처리 정지 요청', '계정 설정 페이지에서 직접 데이터 수정 또는 계정 삭제'],
    },
    {
      heading: '7. 보안 조치',
      paragraphs: ['전송 구간 TLS 암호화, 데이터베이스 접근 제어, 정기 백업 및 무결성 점검 등을 적용합니다.'],
    },
    {
      heading: '8. 문의',
      paragraphs: ['개인정보 관련 문의는 운영자에게 이메일로 연락해 주십시오.'],
    },
  ],
};
