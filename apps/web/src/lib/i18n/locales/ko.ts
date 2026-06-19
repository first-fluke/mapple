/**
 * Message catalog shape — shared between all locales.
 * All values are `string`. Add new keys here first, then mirror in every locale.
 */
export interface Messages {
  nav: {
    globe: string;
    graph: string;
    contacts: string;
    settings: string;
    mainNavLabel: string;
    switchToDark: string;
    switchToLight: string;
  };
  settings: {
    title: string;
    tabs: {
      profile: string;
      appearance: string;
      tags: string;
      export: string;
      account: string;
    };
    profile: {
      title: string;
      description: string;
      emailLabel: string;
      emailHint: string;
      nameLabel: string;
      namePlaceholder: string;
      saveButton: string;
      savingButton: string;
    };
    appearance: {
      title: string;
      description: string;
      themeLabel: string;
      themeHint: string;
      themeSystem: string;
      themeLight: string;
      themeDark: string;
      themeGroupLabel: string;
    };
    tags: {
      title: string;
      description: string;
      newTagLabel: string;
      newTagPlaceholder: string;
      colorPickerLabel: string;
      colorLabel: string;
      editSave: string;
      editCancel: string;
      empty: string;
    };
    export: {
      title: string;
      description: string;
      contactsTitle: string;
      contactsDescription: string;
      downloadButton: string;
      exportingButton: string;
    };
    account: {
      title: string;
      description: string;
      deleteTitle: string;
      deleteDescription: string;
      deleteButton: string;
      deleteDialog: {
        title: string;
        description: string;
        confirmLabel: string;
        confirmPlaceholder: string;
        cancelButton: string;
        deleteButton: string;
        deletingButton: string;
      };
    };
  };
  contacts: {
    title: string;
    searchPlaceholder: string;
    sortNewest: string;
    sortOldest: string;
    sortNameAZ: string;
    sortNameZA: string;
    hasEmailToggleLabel: string;
    hasPhoneToggleLabel: string;
    noInfo: string;
    emptyNoFilter: {
      title: string;
      description: string;
    };
    emptyFiltered: {
      title: string;
      description: string;
    };
    addButton: string;
    detail: {
      back: string;
      globeView: string;
      networkView: string;
      loading: string;
      notFound: string;
      backToList: string;
      invalidId: string;
      tabs: {
        timeline: string;
        meetings: string;
        tags: string;
      };
      timelineTitle: string;
      meetingsTitle: string;
      addMeetingLabel: string;
      addButton: string;
      tagsTitle: string;
    };
    profile: {
      changeAvatarLabel: string;
      fileInputLabel: string;
      uploadingText: string;
      uploadSuccess: string;
      uploadError: string;
      snsProfileLabel: string;
    };
    wizard: {
      title: string;
      stepDescription: string;
      steps: {
        basicInfo: string;
        location: string;
        tagsExperience: string;
      };
      backButton: string;
      nextButton: string;
      createButton: string;
      creatingButton: string;
    };
    basicInfo: {
      nameLabel: string;
      namePlaceholder: string;
      emailLabel: string;
      phoneLabel: string;
      phonePlaceholder: string;
      validationNameRequired: string;
    };
    experience: {
      addTitle: string;
      editTitle: string;
      orgNameLabel: string;
      orgNamePlaceholder: string;
      orgSuggestionsLabel: string;
      roleLabel: string;
      rolePlaceholder: string;
      majorLabel: string;
      majorPlaceholder: string;
      cancelButton: string;
      editButton: string;
      addButton: string;
      count: string;
      empty: string;
      addLabel: string;
      editLabel: string;
      deleteLabel: string;
      validationOrgRequired: string;
      validationInputCheck: string;
      toastAdded: string;
      toastEdited: string;
      toastAddFailed: string;
      toastEditFailed: string;
      toastDeleted: string;
      toastDeleteFailed: string;
    };
    meeting: {
      addTitle: string;
      editTitle: string;
      titleLabel: string;
      titlePlaceholder: string;
      startsAtLabel: string;
      endsAtLabel: string;
      locationLabel: string;
      locationPlaceholder: string;
      notesLabel: string;
      notesPlaceholder: string;
      cancelButton: string;
      editButton: string;
      addButton: string;
      colTitle: string;
      colDate: string;
      colLocation: string;
      colNotes: string;
      colManage: string;
      empty: string;
      editLabel: string;
      deleteLabel: string;
      validationTitleRequired: string;
      validationStartsAtRequired: string;
      validationEndsAtRequired: string;
      validationInputCheck: string;
      toastAdded: string;
      toastEdited: string;
      toastAddFailed: string;
      toastEditFailed: string;
      toastDeleted: string;
      toastDeleteFailed: string;
    };
    tags: {
      addLabel: string;
      addButton: string;
      searchPlaceholder: string;
      removeLabel: string;
      empty: string;
      toastAdded: string;
      toastAddFailed: string;
      toastRemoved: string;
      toastRemoveFailed: string;
    };
  };
  globe: {
    emptyTitle: string;
    emptyDescription: string;
    emptyAriaLabel: string;
    onboarding: {
      title: string;
      description: string;
      getStarted: string;
    };
    globeAriaLabel: string;
    loadingAriaLabel: string;
    loadError: string;
    locationNavLabel: string;
    viewInNetwork: string;
    errorBoundary: {
      globeIconTitle: string;
      webglTitle: string;
      webglDescription: string;
      genericError: string;
    };
  };
  graph: {
    title: string;
    loading: string;
    searchPlaceholder: string;
    clearSearch: string;
    allTypes: string;
    colleague: string;
    classmate: string;
    friend: string;
    other: string;
    emptyTitle: string;
    emptyDescription: string;
    loadError: string;
    networkGraphAriaLabel: string;
    connectionListCaption: string;
    connectionColSource: string;
    connectionColTarget: string;
    connectionColType: string;
  };
  auth: {
    loginTitle: string;
    loginDescription: string;
    continueWithGoogle: string;
    continueWithGitHub: string;
    termsAgreement: string;
    termsLink: string;
    privacyLink: string;
    termsAgreementSuffix: string;
  };
  toasts: {
    close: string;
    notifications: string;
    saved: string;
    saveError: string;
    deleted: string;
    deleteError: string;
    exportError: string;
  };
  validation: {
    emailInvalid: string;
    phoneInvalid: string;
    avatarType: string;
    avatarSize: string;
  };
}

/** Korean (source-of-truth) catalog */
export const ko: Messages = {
  nav: {
    globe: 'Globe',
    graph: 'Graph',
    contacts: '연락처',
    settings: '설정',
    mainNavLabel: '메인 네비게이션',
    switchToDark: '다크 모드로 전환',
    switchToLight: '라이트 모드로 전환',
  },
  settings: {
    title: '설정',
    tabs: {
      profile: '프로필',
      appearance: '테마',
      tags: '태그',
      export: '내보내기',
      account: '계정',
    },
    profile: {
      title: '프로필',
      description: '계정 프로필 정보를 관리합니다.',
      emailLabel: '이메일',
      emailHint: '이메일은 소셜 계정에서 관리됩니다.',
      nameLabel: '표시 이름',
      namePlaceholder: '이름을 입력하세요',
      saveButton: '저장',
      savingButton: '저장 중...',
    },
    appearance: {
      title: '테마',
      description: 'Mapple이 기기에서 어떻게 보일지 설정합니다.',
      themeLabel: '테마',
      themeHint: '라이트, 다크, 또는 시스템 기본값 중 선택하세요.',
      themeSystem: '시스템',
      themeLight: '라이트',
      themeDark: '다크',
      themeGroupLabel: '테마 선택',
    },
    tags: {
      title: '태그',
      description: '연락처를 정리하기 위한 태그를 생성하고 관리합니다.',
      newTagLabel: '새 태그',
      newTagPlaceholder: '태그 이름',
      colorPickerLabel: '색상 선택',
      colorLabel: '색상 {{color}}',
      editSave: '저장',
      editCancel: '취소',
      empty: '태그가 없습니다. 위에서 첫 번째 태그를 만들어 보세요.',
    },
    export: {
      title: '데이터 내보내기',
      description: '데이터를 CSV 파일로 다운로드합니다.',
      contactsTitle: '연락처',
      contactsDescription: '경력 및 조직 정보를 포함한 모든 연락처를 내보냅니다.',
      downloadButton: '다운로드 (CSV)',
      exportingButton: '내보내는 중...',
    },
    account: {
      title: '위험 구역',
      description: '계정에 영향을 미치는 되돌릴 수 없는 작업입니다.',
      deleteTitle: '계정 삭제',
      deleteDescription: '계정과 모든 관련 데이터를 영구적으로 삭제합니다. 이 작업은 취소할 수 없습니다.',
      deleteButton: '계정 삭제',
      deleteDialog: {
        title: '정말로 삭제하시겠습니까?',
        description: '이 작업은 계정, 연락처, 태그 및 모든 관련 데이터를 영구적으로 삭제합니다. 되돌릴 수 없습니다.',
        confirmLabel: '확인을 위해 DELETE를 입력하세요',
        confirmPlaceholder: 'DELETE',
        cancelButton: '취소',
        deleteButton: '계정 삭제',
        deletingButton: '삭제 중...',
      },
    },
  },
  contacts: {
    title: '연락처',
    searchPlaceholder: '연락처 검색...',
    sortNewest: '최신순',
    sortOldest: '오래된순',
    sortNameAZ: '이름 가나다순',
    sortNameZA: '이름 역순',
    hasEmailToggleLabel: '이메일 있음',
    hasPhoneToggleLabel: '전화번호 있음',
    noInfo: '정보 없음',
    emptyNoFilter: {
      title: '연락처가 없습니다',
      description: '연락처를 추가하면 여기에 표시됩니다.',
    },
    emptyFiltered: {
      title: '연락처를 찾을 수 없습니다',
      description: '검색어 또는 필터를 조정해 보세요.',
    },
    addButton: '연락처 추가',
    detail: {
      back: '목록',
      globeView: '글로브 뷰',
      networkView: '관계 뷰',
      loading: '불러오는 중...',
      notFound: '연락처를 찾을 수 없습니다.',
      backToList: '목록으로 돌아가기',
      invalidId: '잘못된 연락처 ID입니다.',
      tabs: {
        timeline: '경력',
        meetings: '미팅',
        tags: '태그',
      },
      timelineTitle: '경력 타임라인',
      meetingsTitle: '미팅',
      addMeetingLabel: '미팅 추가',
      addButton: '추가',
      tagsTitle: '태그',
    },
    profile: {
      changeAvatarLabel: '프로필 사진 변경',
      fileInputLabel: '프로필 사진 파일 선택',
      uploadingText: '프로필 사진을 업로드하는 중입니다...',
      uploadSuccess: '프로필 사진이 변경되었습니다',
      uploadError: '프로필 사진 업로드에 실패했습니다',
      snsProfileLabel: '{{platform}} 프로필 보기',
    },
    wizard: {
      title: '연락처 추가',
      stepDescription: '{{current}} / {{total}}: {{stepName}}',
      steps: {
        basicInfo: '기본 정보',
        location: '위치',
        tagsExperience: '태그 및 경력',
      },
      backButton: '이전',
      nextButton: '다음',
      createButton: '연락처 만들기',
      creatingButton: '만드는 중...',
    },
    basicInfo: {
      nameLabel: '이름',
      namePlaceholder: '연락처 이름',
      emailLabel: '이메일',
      phoneLabel: '전화번호',
      phonePlaceholder: '+82 10-1234-5678',
      validationNameRequired: '이름을 입력해 주세요',
    },
    experience: {
      addTitle: '경력 추가',
      editTitle: '경력 수정',
      orgNameLabel: '조직 이름',
      orgNamePlaceholder: '회사, 학교 등',
      orgSuggestionsLabel: '조직 검색 결과',
      roleLabel: '직책 / 역할',
      rolePlaceholder: '소프트웨어 엔지니어',
      majorLabel: '전공 / 분야',
      majorPlaceholder: '컴퓨터공학',
      cancelButton: '취소',
      editButton: '수정',
      addButton: '추가',
      count: '{{count}}건',
      empty: '아직 경력이 없습니다.',
      addLabel: '경력 추가',
      editLabel: '{{name}} 경력 수정',
      deleteLabel: '{{name}} 경력 삭제',
      validationOrgRequired: '조직 이름을 입력해 주세요',
      validationInputCheck: '조직을 선택하거나 입력해 주세요',
      toastAdded: '경력이 추가되었습니다',
      toastEdited: '경력이 수정되었습니다',
      toastAddFailed: '경력 추가에 실패했습니다',
      toastEditFailed: '경력 수정에 실패했습니다',
      toastDeleted: '경력이 삭제되었습니다',
      toastDeleteFailed: '경력 삭제에 실패했습니다',
    },
    meeting: {
      addTitle: '미팅 추가',
      editTitle: '미팅 수정',
      titleLabel: '제목',
      titlePlaceholder: '미팅 제목',
      startsAtLabel: '시작 일시',
      endsAtLabel: '종료 일시',
      locationLabel: '장소',
      locationPlaceholder: '회의실, 카페 등',
      notesLabel: '메모',
      notesPlaceholder: '미팅 내용, 결정 사항 등',
      cancelButton: '취소',
      editButton: '수정',
      addButton: '추가',
      colTitle: '제목',
      colDate: '날짜',
      colLocation: '장소',
      colNotes: '메모',
      colManage: '관리',
      empty: '아직 미팅이 없습니다.',
      editLabel: '{{name}} 미팅 수정',
      deleteLabel: '{{name}} 미팅 삭제',
      validationTitleRequired: '제목을 입력해 주세요',
      validationStartsAtRequired: '시작 일시를 입력해 주세요',
      validationEndsAtRequired: '종료 일시를 입력해 주세요',
      validationInputCheck: '입력값을 확인해 주세요',
      toastAdded: '미팅이 추가되었습니다',
      toastEdited: '미팅이 수정되었습니다',
      toastAddFailed: '미팅 추가에 실패했습니다',
      toastEditFailed: '미팅 수정에 실패했습니다',
      toastDeleted: '미팅이 삭제되었습니다',
      toastDeleteFailed: '미팅 삭제에 실패했습니다',
    },
    tags: {
      addLabel: '태그 추가',
      addButton: '태그 추가',
      searchPlaceholder: '태그 검색...',
      removeLabel: '{{name}} 태그 제거',
      empty: '태그가 없습니다. 설정에서 태그를 만들어 보세요.',
      toastAdded: '태그가 추가되었습니다',
      toastAddFailed: '태그 추가에 실패했습니다',
      toastRemoved: '태그가 제거되었습니다',
      toastRemoveFailed: '태그 제거에 실패했습니다',
    },
  },
  globe: {
    emptyTitle: '위치 정보가 없습니다',
    emptyDescription: '연락처에 위치(도시 또는 국가)를 추가하면 지구본에서 확인할 수 있습니다.',
    emptyAriaLabel: '연락처 위치 없음',
    onboarding: {
      title: 'Mapple에 오신 것을 환영합니다',
      description: '지구본이 비어 있습니다. 첫 번째 연락처를 추가하여 세계 각지의 인맥을 지도에 표시해 보세요.',
      getStarted: '첫 번째 연락처 추가',
    },
    globeAriaLabel: '지구본 — 연락처 위치 시각화',
    loadingAriaLabel: '지구본 로딩 중',
    loadError: '연락처 데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.',
    locationNavLabel: '위치 기반 연락처 목록',
    viewInNetwork: '네트워크 그래프에서 보기',
    errorBoundary: {
      globeIconTitle: '지구본 아이콘',
      webglTitle: '3D 지구본을 표시할 수 없습니다',
      webglDescription:
        '브라우저가 WebGL을 지원하지 않거나 그래픽 드라이버 문제가 있습니다.\nChrome 또는 Firefox 최신 버전에서 다시 시도해 주세요.',
      genericError: '지구본을 불러오지 못했습니다. 페이지를 새로고침해 주세요.',
    },
  },
  graph: {
    title: '관계 그래프',
    loading: '그래프를 불러오는 중...',
    searchPlaceholder: '연락처 검색...',
    clearSearch: '검색 지우기',
    allTypes: '모든 유형',
    colleague: '동료',
    classmate: '학우',
    friend: '친구',
    other: '기타',
    emptyTitle: '아직 연결이 없습니다',
    emptyDescription: '연락처와 경력을 추가하면 관계 그래프를 볼 수 있습니다.',
    loadError: '데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.',
    networkGraphAriaLabel: '관계 네트워크 그래프',
    connectionListCaption: '관계 연결 목록',
    connectionColSource: '출발',
    connectionColTarget: '도착',
    connectionColType: '관계 유형',
  },
  auth: {
    loginTitle: 'Mapple',
    loginDescription: '계정에 로그인하세요',
    continueWithGoogle: 'Google로 계속하기',
    continueWithGitHub: 'GitHub으로 계속하기',
    termsAgreement: '로그인 시',
    termsLink: '이용약관',
    privacyLink: '개인정보처리방침',
    termsAgreementSuffix: '에 동의하는 것으로 간주됩니다.',
  },
  toasts: {
    close: '닫기',
    notifications: '알림',
    saved: '저장되었습니다',
    saveError: '저장에 실패했습니다',
    deleted: '삭제되었습니다',
    deleteError: '삭제에 실패했습니다',
    exportError: '내보내기에 실패했습니다',
  },
  validation: {
    emailInvalid: '올바른 이메일 주소를 입력해 주세요',
    phoneInvalid: '올바른 전화번호 형식이 아닙니다 (예: +82 10-1234-5678)',
    avatarType: 'JPEG, PNG, WebP 파일만 업로드할 수 있습니다',
    avatarSize: '파일 크기는 5MB 이하여야 합니다',
  },
};

/** Alias kept for backwards-compatibility with `import type { Dictionary }` */
export type Dictionary = Messages;
