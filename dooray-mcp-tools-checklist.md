# Dooray MCP Tools 체크리스트

## API 기본 정보
- **Base URL**: `https://api.dooray.com`
- **인증 방식**: `Authorization: dooray-api {인증토큰}` 헤더
- **응답 형식**: JSON

## 📋 Task/Project Management (확인된 API)
- [x] **프로젝트 조회** - `GET /project/v1/projects/{projectId}` - 프로젝트 정보 조회
- [ ] **프로젝트 목록 조회** - 사용자가 속한 프로젝트 목록

### 업무(Task) 관리
- [ ] **업무 목록 조회** - 프로젝트별 업무 리스트
- [ ] **업무 상세 조회** - 특정 업무의 상세 정보
- [ ] **업무 생성** - 새 업무 생성
- [ ] **업무 수정** - 업무 내용/상태 수정
- [ ] **업무 삭제** - 업무 삭제
- [ ] **업무 상태 변경** - 진행중/완료 등 상태 업데이트
- [ ] **담당자 지정/변경** - 업무 담당자 할당
- [ ] **업무 우선순위 설정** - 우선순위 변경

### 태그
- [ ] **태그 조회** - 사용 가능한 태그 목록
- [ ] **태그 추가** - 업무에 태그 추가
- [ ] **태그 제거** - 업무에서 태그 제거
- [ ] **태그 생성** - 새 태그 생성

## 💬 댓글/커뮤니케이션
- [ ] **댓글 조회** - 업무의 댓글 목록
- [ ] **댓글 작성** - 업무에 댓글 추가
- [ ] **댓글 수정** - 기존 댓글 수정
- [ ] **댓글 삭제** - 댓글 제거
- [ ] **멘션** - 사용자 태그/알림

## 🔍 검색/조회
- [ ] **업무 검색** - 업무 내용/제목 검색
- [ ] **프로젝트별 업무 조회** - 특정 프로젝트의 업무 목록
- [ ] **담당자별 업무 조회** - 특정 멤버의 업무 목록
- [ ] **상태별 업무 조회** - 진행중/완료/대기 등 상태별 조회
- [ ] **태그별 업무 조회** - 특정 태그가 달린 업무 목록
- [ ] **기간별 업무 조회** - 특정 기간 내 업무 조회

## 👥 멤버 관리 (확인된 API)
- [x] **멤버 검색 (이메일)** - `GET /common/v1/members?externalEmailAddresses={email}` - 이메일로 멤버 검색
- [x] **멤버 검색 (ID)** - `GET /common/v1/members?userCode={userId}` - 사용자 ID로 멤버 검색

## 🔐 인증/권한
- [ ] **OAuth 인증** - OAuth 2.0 인증
- [ ] **API 토큰 발급** - API 액세스 토큰
- [ ] **권한 확인** - API 접근 권한 확인

---

## 우선순위 추천 (MCP Tools)

### 🎯 필수 기능 (High Priority)
1. **업무 목록 조회** - 프로젝트별 업무 리스트
2. **업무 상세 조회** - 특정 업무의 상세 정보
3. **업무 생성** - 새 업무 생성
4. **업무 수정** - 업무 내용/상태 수정
5. **프로젝트 정보 조회** ✅ - `GET /project/v1/projects/{projectId}`
6. **멤버 검색** ✅ - `GET /common/v1/members`

### 🔄 주요 기능 (Medium Priority)
1. **댓글 조회** - 업무의 댓글 목록
2. **댓글 작성** - 업무에 댓글 추가
3. **태그 조회** - 사용 가능한 태그 목록
4. **태그 추가/제거** - 업무에 태그 관리
5. **업무 검색** - 업무 내용/제목 검색

### ➕ 추가 기능 (Low Priority)
1. **담당자별 업무 조회** - 특정 멤버의 업무 목록
2. **상태별 업무 조회** - 진행중/완료/대기 등 상태별 조회
3. **태그별 업무 조회** - 특정 태그가 달린 업무 목록
4. **댓글 수정/삭제** - 댓글 관리
5. **멘션 기능** - 사용자 태그/알림

---

## 구현 시 고려사항

### 기술적 요구사항
- [ ] REST API 지원 여부
- [ ] GraphQL API 지원 여부
- [ ] WebSocket 실시간 통신
- [ ] Rate Limiting 정책
- [ ] 페이지네이션 지원
- [ ] 벌크 작업 지원

### 인증 방식
- [ ] OAuth 2.0
- [ ] API Key
- [ ] JWT Token
- [ ] Session 기반

### 응답 형식
- [ ] JSON
- [ ] XML
- [ ] 파일 스트리밍

---

## MCP Tools 구현 방안 (5개 Tool 기반)

### 1. 업무(Task) 관리 Tool
```typescript
{
  name: "dooray_tasks",
  description: "Manage Dooray tasks - list, get details, create, update, delete, change status, assign members",
  parameters: {
    type: "object",
    properties: {
      action: { 
        type: "string", 
        enum: ["list", "get", "create", "update", "delete", "change_status", "assign"],
        description: "Action to perform" 
      },
      projectId: { type: "string", description: "Project ID (required for most actions)" },
      taskId: { type: "string", description: "Task ID (required for get/update/delete/status/assign)" },
      title: { type: "string", description: "Task title (for create/update)" },
      description: { type: "string", description: "Task description (for create/update)" },
      status: { type: "string", description: "Task status (for create/update/change_status)" },
      assigneeId: { type: "string", description: "Assignee member ID (for assign action)" },
      priority: { type: "string", description: "Task priority (for create/update)" }
    },
    required: ["action"]
  }
}
```

### 2. 댓글(Comments) 관리 Tool
```typescript
{
  name: "dooray_comments",
  description: "Manage Dooray task comments - get list, create, update, delete comments with mention support",
  parameters: {
    type: "object",
    properties: {
      action: { 
        type: "string", 
        enum: ["list", "create", "update", "delete"],
        description: "Action to perform on comments" 
      },
      taskId: { type: "string", description: "Task ID (required)" },
      commentId: { type: "string", description: "Comment ID (required for update/delete)" },
      content: { type: "string", description: "Comment content (for create/update)" },
      mentions: { type: "array", items: { type: "string" }, description: "User IDs to mention (optional)" }
    },
    required: ["action", "taskId"]
  }
}
```

### 3. 태그(Tags) 관리 Tool
```typescript
{
  name: "dooray_tags",
  description: "Manage Dooray tags - list available tags, create new tags, add/remove tags from tasks",
  parameters: {
    type: "object",
    properties: {
      action: { 
        type: "string", 
        enum: ["list", "create", "add_to_task", "remove_from_task"],
        description: "Action to perform on tags" 
      },
      projectId: { type: "string", description: "Project ID (required for list/create)" },
      taskId: { type: "string", description: "Task ID (required for add_to_task/remove_from_task)" },
      tagName: { type: "string", description: "Tag name (for create/add_to_task/remove_from_task)" },
      tagColor: { type: "string", description: "Tag color (for create action, optional)" }
    },
    required: ["action"]
  }
}
```

### 4. 검색(Search) Tool
```typescript
{
  name: "dooray_search",
  description: "Search Dooray content - tasks by various criteria, filter by status/assignee/tags/date range",
  parameters: {
    type: "object",
    properties: {
      searchType: { 
        type: "string", 
        enum: ["tasks", "by_assignee", "by_status", "by_tag", "by_date_range"],
        description: "Type of search to perform" 
      },
      projectId: { type: "string", description: "Project ID (required for most searches)" },
      query: { type: "string", description: "Search query text (for tasks search)" },
      assigneeId: { type: "string", description: "Assignee ID (for by_assignee search)" },
      status: { type: "string", description: "Task status (for by_status search)" },
      tagName: { type: "string", description: "Tag name (for by_tag search)" },
      startDate: { type: "string", description: "Start date (for by_date_range search)" },
      endDate: { type: "string", description: "End date (for by_date_range search)" },
      limit: { type: "integer", description: "Maximum results to return (optional)" }
    },
    required: ["searchType"]
  }
}
```

### 5. 사람(Members) 관리 Tool
```typescript
{
  name: "dooray_members",
  description: "Manage Dooray members - search by email/ID, get member details, check project membership",
  parameters: {
    type: "object",
    properties: {
      action: { 
        type: "string", 
        enum: ["search_by_email", "search_by_id", "get_details", "list_project_members"],
        description: "Action to perform on members" 
      },
      email: { type: "string", description: "Email address (for search_by_email)" },
      userId: { type: "string", description: "User ID (for search_by_id/get_details)" },
      projectId: { type: "string", description: "Project ID (for list_project_members)" }
    },
    required: ["action"]
  }
}
```

## 사용 방법
1. 위 체크리스트에서 필요한 기능들을 선택하세요
2. 우선순위를 고려하여 구현 순서를 정하세요 (업무 관리 → 댓글 → 태그 → 검색)
3. MCP tools 구현을 시작하세요

## 참고 자료
- **공식 API 문서**: https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419
- **Python 라이브러리**: PyDooray (https://pypi.org/project/PyDooray/)
- **Node.js 예제**: https://github.com/jason07289/DoorayBot
- API 버전과 deprecated 여부를 확인하세요
- Rate limit과 quota를 고려한 구현이 필요합니다